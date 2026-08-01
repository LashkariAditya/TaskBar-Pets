; ─────────────────────────────────────────────────────────────────────────────
; TaskbarPets.iss  —  Inno Setup Installer Script
; Creates a proper Windows Setup.exe  (like TranslucentTB, Wallpaper Engine)
; Download Inno Setup free from: https://jrsoftware.org/isinfo.php
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "Taskbar Pets"
#define AppVersion   "1.0.0"
#define AppPublisher "Your Name"
#define AppURL       "https://github.com/yourname/taskbar-pets"
#define AppExeName   "TaskbarPets.exe"
#define AppDataName  "TaskbarPets"

[Setup]
AppId={{A3F7B2C1-1234-4567-89AB-CDEF01234567}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; No UAC prompt for user-level install
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer_output
OutputBaseFilename=TaskbarPets_Setup_v{#AppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
; Modern dark-look wizard
WizardImageFile=assets\installer_banner.bmp
WizardSmallImageFile=assets\installer_icon.bmp
DisableProgramGroupPage=yes
CloseApplications=yes
UninstallDisplayIcon={app}\{#AppExeName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=Pokemon Desktop Companions for Windows Taskbar
VersionInfoProductName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Create a &Desktop shortcut";     GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startupicon";   Description: "Start &automatically with Windows (silent)"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Main executable (built by build.bat / PyInstaller)
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Config template (will be copied to %APPDATA%\TaskbarPets on first run)
Source: "config.json";         DestDir: "{app}";  Flags: ignoreversion; DestName: "config.default.json"

; Silent launcher VBS script (backup)
Source: "run_silent.vbs";      DestDir: "{app}";  Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Launch the app after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent

[Registry]
; Startup registry entry (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run";
    ValueType: string; ValueName: "{#AppName}";
    ValueData: """{app}\{#AppExeName}""";
    Flags: uninsdeletevalue; Tasks: startupicon

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\{#AppDataName}"

[Code]
// Show nice welcome message
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Caption :=
    'This will install Taskbar Pets ' + '{#AppVersion}' + ' on your computer.'#13#10#13#10 +
    'Taskbar Pets brings animated Pok' + #233 + 'mon companions to your Windows taskbar.'#13#10#13#10 +
    'No Python required  —  just install and enjoy!';
end;
