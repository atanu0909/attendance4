#!/bin/bash

# Railway startup script for Device 19 Attendance Monitor
# Installs ODBC drivers and starts the monitoring service

echo "🚀 Starting Railway deployment for Device 19 Attendance Monitor..."

# Install ODBC drivers if not already installed
if ! command -v odbcinst &> /dev/null; then
    echo "📦 Installing ODBC drivers..."
    
    # Update package list
    apt-get update
    
    # Install basic dependencies
    apt-get install -y curl apt-transport-https ca-certificates gnupg lsb-release unixodbc unixodbc-dev
    
    # Add Microsoft repository
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
    
    # Update package list again
    apt-get update
    
    # Install Microsoft ODBC drivers
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 msodbcsql17
    
    echo "✅ ODBC drivers installed successfully"
else
    echo "✅ ODBC drivers already available"
fi

# List available drivers
echo "🔍 Available ODBC drivers:"
odbcinst -q -d

# Start the monitoring application
echo "🎯 Starting attendance monitoring service..."
python railway_monitor.py
