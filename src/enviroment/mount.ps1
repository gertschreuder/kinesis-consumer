# Use this to bring up local stack on your dev box.
Param
(
	[Parameter(mandatory=$false)] [AllowNull()] [string]$region,
	[Parameter(mandatory=$false)] [AllowNull()] [switch]$pull,
	[Parameter(mandatory=$false)] [AllowNull()] [switch]$remove,
	[Parameter(mandatory=$false)] [AllowNull()] [switch]$mount,
	[Parameter(mandatory=$false)] [AllowNull()] [switch]$update
)
if (($region -eq $region) -or ($region -eq "")){
	$region = "eu-west-1"
}

# read port mappings
$localstackConfig = Get-Content ".\src\enviroment\localstack.json"
$localstackConfig = "$localstackConfig" | 
	ConvertFrom-Json |
	Select -expand localStack |
	Select DynamoDB, SQS

$portMappings = ""
$portMappings = "$portMappings -p " + $localstackConfig.DynamoDB + ":4569"
$portMappings = "$portMappings -p " + $localstackConfig.SQS + ":4576"

if ($pull -eq $true){
	docker pull localstack/localstack
}
if (($pull -eq $true) -or ($remove -eq $true) -or ($mount -eq $true)){
	docker stop localstack
}
if ($remove -eq $true){
	docker rm localstack
}
if ($mount -eq $true){
	Invoke-Expression "docker run -d --name localstack $portMappings localstack/localstack"
}
if ($update -eq $true){
	$dynamoEndpoint = "http://localhost:" + $localstackConfig.DynamoDB
	$expression = ".\src\enviroment\updateDynamoDB.ps1 -awsProfile:""default"" -awsRegion:""$region"" -endPointUrl:""$dynamoEndpoint"" -teardown -upgrade"
	Invoke-Expression $expression
}