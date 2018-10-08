Param
(
	[Parameter(mandatory=$false)] [AllowNull()] [string]$awsProfile,
	[Parameter(mandatory=$false)] [AllowNull()] [string]$awsRegion,
	[Parameter(mandatory=$false)] [AllowNull()] [string]$endPointUrl,
    [Parameter(mandatory=$false)] [AllowNull()] [switch]$teardown,
    [Parameter(mandatory=$false)] [AllowNull()] [switch]$upgrade
)

# Prepare the command template with profile and endpoint options
$dbCommandTemplate = 'aws dynamodb ##command##'
if (($awsProfile -ne $null) -and ($awsProfile -ne "")){
    $dbCommandTemplate = $dbCommandTemplate + ' --profile ' + $awsProfile
}
if (($endPointUrl -ne $null) -and ($endPointUrl -ne "")){
	$useLocalEndpoint = $true
	$dbCommandTemplate = $dbCommandTemplate + ' --endpoint-url ' + $endPointUrl
}

# Set local variable defaults
$dbWasChanged = $false
$tablesList = "".Split(" ")
$scriptsPath = ".\src\enviroment\"
$scriptFilePattern = "(^\d*.\d*.\d*.\d*_\d+)";
$divider = "--------------------------------------------------"

# Commandlet to execute commands using the prepared template
function ExecuteDynamoCommand {
    [CmdletBinding()]
    param
    (
        [Parameter(mandatory=$true)] [ValidateNotNullOrEmpty()] [string]$dbCommand
    )
    $commandExpression = $dbCommandTemplate -replace '##command##', $dbCommand
    $commandResult = Invoke-Expression $commandExpression
    return "$commandResult"
}

function ExecuteDynamoCommandWithException {
    [CmdletBinding()]
    param
    (
        [Parameter(mandatory=$true)] [ValidateNotNullOrEmpty()] [string]$dbCommand
    )

	try{
		$commandExpression = $dbCommandTemplate -replace '##command##', $dbCommand
		$commandResult = Invoke-Expression $commandExpression 2>&1
	    return "$commandResult"
	}
	catch{
		$errorResult = $_.Exception.Message
	    return "$errorResult"
	}
}

# Commandlet to retrieve list of tables
function GetDBTables {
    $tablesResult = ExecuteDynamoCommand -dbCommand:"list-tables"
	$tablesResult = "$tablesResult" | 
		ConvertFrom-Json | 
		Select -expand TableNames |
		where { $_.StartsWith("Dev") }

    if ($tablesResult -eq $null) {
        $tablesResult = ""
    }
    $tablesResult = $tablesResult.Split(" ")
	if (($tablesResult.Length -eq 1) -and ($tablesResult[0] -eq "")) {
		$tablesResult = @()
		Write-Host "-- No tables in DB"
	}

    return $tablesResult
}

# Commandlet to batch execute from file
function ExecuteFileCommands {
    [CmdletBinding()]
    param
    (
        [Parameter(mandatory=$true)] [ValidateNotNullOrEmpty()] [string]$commandsFile
    )
    $fileCommands = [string[]](Get-Content -Path $commandsFile)
    foreach($fileCommand in $fileCommands){
        if ($fileCommand -ne "") {			
            if ($fileCommand.StartsWith("#waittableactive#")){
                $tableName = $fileCommand -replace '#waittableactive#', ''
                $waitTableExpression = "describe-table --table-name $tableName"
                Write-Host "--- Wait for table '$tableName' to become active"
                $isActive=$false
                While(-not $isActive){
                    $awaitTableResult = ExecuteDynamoCommand -dbCommand:$waitTableExpression
                    $tableStatus = "$awaitTableResult" | ConvertFrom-Json | Select -expand Table | Select TableStatus
                    if ("$tableStatus".Contains("ACTIVE")){
					    $isActive = $true
				    }
				    else{
					    sleep 2
				    }
			    }
                Write-Host "--- Table '$tableName' is now active."
            }
            elseif ($fileCommand.StartsWith("#waittabledeactivate#")){
				$tableName = $fileCommand -replace '#waittabledeactivate#', ''
				$waitTableExpression = "describe-table --table-name $tableName"
				Write-Host "--- Wait for table '$tableName' to deactivate"
				$isActive=$true
				While($isActive){
					$awaitTableResult = ExecuteDynamoCommandWithException -dbCommand:$waitTableExpression
					if ("$awaitTableResult".Contains("ResourceNotFoundException")){
						$isActive=$false
					}
					else {
						$tableStatus = "$awaitTableResult" | ConvertFrom-Json | Select -expand Table | Select TableStatus
						if ("$tableStatus".Contains("ACTIVE") -or "$tableStatus".Contains("DELETING") -or "$tableStatus".Contains("UPDATING")){
							sleep 2
						}
						else{
							$isActive=$false
						}
					}
				}
				Write-Host "--- Table '$tableName' is now deactivate."
			}
            else {
                if ($fileCommand.StartsWith("#remoteonly#")){
                    $fileCommand = $fileCommand -replace '#remoteonly#', ''
                    if ($useLocalEndpoint -ne $true){
                        Write-Host "--- =>" $fileCommand
                        $fileCommandResult = ExecuteDynamoCommand -dbCommand:$fileCommand
				    }
				    else{
					    Write-Host "--- => [Skipped]" $fileCommand 
				    }
			    }
			    else{
                    Write-Host "--- =>" $fileCommand
                    $fileCommandResult = ExecuteDynamoCommand -dbCommand:$fileCommand
			    }
            }
        }
    }
}

# Get tables and current version of database
$tablesList = GetDBTables
Write-Host "Tables: $tablesList"
Write-Host $divider

# If database not empty and teardown switch set... delete all tables
if ($teardown -eq $true){
	Write-Host "- Deleting tables from database"
		$tablesList | ForEach {
			if (("$_" -ne "") -and ("$_" -ne $null)){
				$deleteCommand = "delete-table --table-name $_"
				Write-Host "--- =>" $deleteCommand
				ExecuteDynamoCommand -dbCommand:$deleteCommand
				$dbWasChanged = $true
			}
		}
		$allTablesDropped = $false
		While(-not $allTablesDropped) {
			$tablesList = GetDBTables
			if ($tablesList.Length -le 0) {
				$allTablesDropped = $true
			} 
			else { 
				sleep 1
			}
		}
		Write-Host "- All tables deleted."
		Write-Host $divider
}

# If upgrade switch set... run update scripts between db and target versions
if ($upgrade -eq $true){
    
	Write-Host "- Preparing upgrade scripts"	
    
	Get-ChildItem $scriptsPath -Include *.txt, *.ps1 -Recurse | Sort-Object BaseName | ForEach-Object {
		Write-Host $_.BaseName
		if ($_.BaseName -match $scriptFilePattern){
			if ($_.Extension -eq ".txt") {
				Write-Host "-- Reading commands from" $_.Name
				ExecuteFileCommands -commandsFile:$_.FullName
			}
		}                
	}

	$dbWasChanged = $true

    Write-Host "- Cleaning up upgrade scripts"
    
    Write-Host $divider
}

# Refresh DB version to report final version
if ($dbWasChanged -eq $true) {
	$tablesList = GetDBTables
}