[Setup]
AppName=SanGlow
AppVersion=1.0.9
AppPublisher=AlexGoster
AppPublisherURL=https://github.com/AlexGoster/SanGlow
AppSupportURL=https://github.com/AlexGoster/SanGlow/issues
AppUpdatesURL=https://github.com/AlexGoster/SanGlow/releases
AppCopyright=Copyright (c) 2024-2026 AlexGoster
VersionInfoVersion=1.0.9.0
VersionInfoDescription=SanGlow Music Player
VersionInfoProductName=SanGlow
VersionInfoProductVersion=1.0.9
DefaultDirName={autopf}\SanGlow
DefaultGroupName=SanGlow
OutputDir=installer_output
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\SanGlow.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=10.0
OutputBaseFilename=sanglow_setup
WizardStyle=modern
CloseApplications=force
CloseApplicationsFilter=SanGlow.exe
RestartApplications=no
AllowCancelDuringInstall=yes
ChangesAssociations=no
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableStartupPrompt=yes
DisableDirPage=no
DisableFinishedPage=no
WindowVisible=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\__pycache__"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\SanGlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\SanGlow"; Filename: "{app}\SanGlow.exe"
Name: "{group}\{cm:UninstallProgram,SanGlow}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SanGlow"; Filename: "{app}\SanGlow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SanGlow.exe"; Description: "{cm:LaunchProgram,SanGlow}"; Flags: nowait postinstall skipifsilent shellexec
