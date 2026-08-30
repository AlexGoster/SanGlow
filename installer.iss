[Setup]
AppName=SanGlow
AppVersion=1.0.0
AppPublisher=Sanek
AppCopyright=2024-2026 Sanek
DefaultDirName={autopf}\SanGlow
DefaultGroupName=SanGlow
OutputDir=installer_output
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\SanGlow.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\SanGlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SanGlow"; Filename: "{app}\SanGlow.exe"
Name: "{group}\{cm:UninstallProgram,SanGlow}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SanGlow"; Filename: "{app}\SanGlow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SanGlow.exe"; Description: "{cm:LaunchProgram,SanGlow}"; Flags: nowait postinstall skipifsilent
