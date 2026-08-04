# Run this script in PowerShell as Administrator
# Right-click PowerShell -> Run as Administrator, then:
#   cd C:\Users\LENOVO\OneDrive\Documents\CSM\Complain-Management-System
#   .\install_mysql_admin.ps1

Write-Host "Installing MariaDB (MySQL-compatible)..." -ForegroundColor Green

# Option 1: Chocolatey (recommended)
choco install mariadb --params='/allowEmptyPassword' -y --force

if ($LASTEXITCODE -ne 0) {
    Write-Host "Chocolatey failed. Trying direct download..." -ForegroundColor Yellow
    # Option 2: Direct MSI download
    $msiUrl = "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.39.0.msi"
    $msiPath = "$env:TEMP\mysql-installer.msi"
    Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing
    Start-Process msiexec.exe -Wait -ArgumentList "/i $msiPath /quiet"
}

Write-Host "Done! Check if MySQL service is running:" -ForegroundColor Green
Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Select-Object Name, Status
