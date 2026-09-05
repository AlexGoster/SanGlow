[Setup]
AppName=SanGlow
AppVersion=1.3.0
AppPublisher=AlexGoster
AppPublisherURL=https://github.com/AlexGoster/SanGlow
AppSupportURL=https://github.com/AlexGoster/SanGlow/issues
AppUpdatesURL=https://github.com/AlexGoster/SanGlow/releases
AppCopyright=Copyright (c) 2024-2026 AlexGoster
VersionInfoVersion=1.3.0.0
VersionInfoDescription=SanGlow Music Player
VersionInfoProductName=SanGlow
VersionInfoProductVersion=1.3.0
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
UsePreviousAppDir=yes
InfoBeforeFile=web\index.html
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{localappdata}\SanGlow"
Type: filesandordirs; Name: "{localappdata}\sanglow"
Type: filesandordirs; Name: "{app}\*.db"
Type: filesandordirs; Name: "{app}\settings.json"
Type: filesandordirs; Name: "{app}\config"
Type: filesandordirs; Name: "{app}\web"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "cleandata"; Description: "Remove all previous user data and settings"; GroupDescription: "Cleanup:"; Flags: unchecked

[Files]
Source: "dist\SanGlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "web\*"; DestDir: "{app}\web"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SanGlow"; Filename: "{app}\SanGlow.exe"
Name: "{group}\{cm:UninstallProgram,SanGlow}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SanGlow"; Filename: "{app}\SanGlow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SanGlow.exe"; Description: "{cm:LaunchProgram,SanGlow}"; Flags: nowait postinstall skipifsilent shellexec

[Code]
function KillProcessByName(const FileName: string): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('taskkill', '/f /im ' + FileName, '', 0, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    KillProcessByName('SanGlow.exe');
    KillProcessByName('SanGlow-x64.exe');
    Exec('taskkill', '/f /im SanGlow.exe', '', 0, ewWaitUntilTerminated, ResultCode);
    Exec('taskkill', '/f /im SanGlow-x64.exe', '', 0, ewWaitUntilTerminated, ResultCode);
    Sleep(500);
    DelTree(ExpandConstant('{app}\_internal'), True, True, True);
  end;
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('cleandata') then
  begin
    DelTree(ExpandConstant('{localappdata}\SanGlow'), True, True, True);
    DelTree(ExpandConstant('{localappdata}\sanglow'), True, True, True);
    DelTree(ExpandConstant('{app}\data'), True, True, True);
    DelTree(ExpandConstant('{app}\config'), True, True, True);
    DeleteFile(ExpandConstant('{app}\settings.json'));
    DeleteFile(ExpandConstant('{app}\*.db'));
  end;
end;
