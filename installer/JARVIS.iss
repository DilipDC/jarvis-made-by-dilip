#define AppName "JARVIS — BUILT BY DILIP"
#define AppVersion "1.0.0"
#define AppExeName "JARVIS.exe"
[Setup]
AppId={{C5A3D5B7-6B0E-4E68-9E4A-9B9B5A9E10A1}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\JARVIS
DefaultGroupName=JARVIS
OutputDir=dist
OutputBaseFilename=JARVIS-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
[Files]
Source: "..\dist\JARVIS.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\JARVIS"; Filename: "{app}\{#AppExeName}"
[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch JARVIS"; Flags: nowait postinstall skipifsilent
