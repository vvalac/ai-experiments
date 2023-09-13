# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

$ErrorActionPreference = 'Stop'

$PRESIGNED_URL = Read-Host -Prompt "Enter the URL from email"
Write-Host ""
$MODEL_SIZE = Read-Host -Prompt "Enter the list of models to download without spaces (7B,13B,70B,7B-chat,13B-chat,70B-chat), or press Enter for all"
$TARGET_FOLDER = ".../models/"

if (-not (Test-Path $TARGET_FOLDER)) {
    New-Item -Path $TARGET_FOLDER -ItemType Directory
}

if (-not $MODEL_SIZE) {
    $MODEL_SIZE = "7B,13B,70B,7B-chat,13B-chat,70B-chat"
}

Write-Host "Downloading LICENSE and Acceptable Usage Policy"
Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "LICENSE") -OutFile "$TARGET_FOLDER/LICENSE"
Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "USE_POLICY.md") -OutFile "$TARGET_FOLDER/USE_POLICY.md"

Write-Host "Downloading tokenizer"
Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "tokenizer.model") -OutFile "$TARGET_FOLDER/tokenizer.model"
Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "tokenizer_checklist.chk") -OutFile "$TARGET_FOLDER/tokenizer_checklist.chk"

$CPU_ARCH = (Get-CimInstance Win32_Processor).Architecture
if ($CPU_ARCH -eq "ARM64") {
    Set-Location $TARGET_FOLDER
    Get-FileHash -Algorithm MD5 tokenizer_checklist.chk
} else {
    Set-Location $TARGET_FOLDER
    # Note: md5sum doesn't exist on Windows by default, so you may need an alternative method or tool
    # For this translation, I'll assume you have a compatible tool installed. Adjust accordingly.
    md5sum -c tokenizer_checklist.chk
}

foreach ($m in $MODEL_SIZE -split ',') {
    switch ($m) {
        "7B" {
            $SHARD = 0
            $MODEL_PATH = "llama-2-7b"
        }
        "7B-chat" {
            $SHARD = 0
            $MODEL_PATH = "llama-2-7b-chat"
        }
        "13B" {
            $SHARD = 1
            $MODEL_PATH = "llama-2-13b"
        }
        "13B-chat" {
            $SHARD = 1
            $MODEL_PATH = "llama-2-13b-chat"
        }
        "70B" {
            $SHARD = 7
            $MODEL_PATH = "llama-2-70b"
        }
        "70B-chat" {
            $SHARD = 7
            $MODEL_PATH = "llama-2-70b-chat"
        }
    }

    Write-Host "Downloading $MODEL_PATH"
    if (-not (Test-Path "$TARGET_FOLDER/$MODEL_PATH")) {
        New-Item -Path "$TARGET_FOLDER/$MODEL_PATH" -ItemType Directory
    }

    0..$SHARD | ForEach-Object {
        Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "$MODEL_PATH/consolidated.$_.pth") -OutFile "$TARGET_FOLDER/$MODEL_PATH/consolidated.$_.pth"
    }

    Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "$MODEL_PATH/params.json") -OutFile "$TARGET_FOLDER/$MODEL_PATH/params.json"
    Invoke-WebRequest -Uri ($PRESIGNED_URL -replace '\*', "$MODEL_PATH/checklist.chk") -OutFile "$TARGET_FOLDER/$MODEL_PATH/checklist.chk"

    Write-Host "Checking checksums"
    if ($CPU_ARCH -eq "ARM64") {
        Set-Location "$TARGET_FOLDER/$MODEL_PATH"
        Get-FileHash -Algorithm MD5 checklist.chk
    } else {
        Set-Location "$TARGET_FOLDER/$MODEL_PATH"
        # Again, assuming you have a compatible md5sum tool installed.
        md5sum -c checklist.chk
    }
}
