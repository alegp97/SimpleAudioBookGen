[Setup]
; App Information
AppName=SimpleAudioBookGen
AppVersion=0.2.0
AppPublisher=AudioBookGen Team
AppPublisherURL=https://github.com/your-repo/audiobook_gen
AppSupportURL=https://github.com/your-repo/audiobook_gen/issues
AppUpdatesURL=https://github.com/your-repo/audiobook_gen/releases

; Base Configuration
DefaultDirName={autopf}\SimpleAudioBookGen
DefaultGroupName=SimpleAudioBookGen
DisableProgramGroupPage=yes

; Output Configuration
OutputDir=installers
OutputBaseFilename=SimpleAudioBookGen_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Execution Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The main executable and all bundled PyInstaller files
Source: "dist\SimpleAudioBookGen\SimpleAudioBookGen.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SimpleAudioBookGen\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\SimpleAudioBookGen"; Filename: "{app}\SimpleAudioBookGen.exe"
Name: "{autodesktop}\SimpleAudioBookGen"; Filename: "{app}\SimpleAudioBookGen.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SimpleAudioBookGen.exe"; Description: "{cm:LaunchProgram,SimpleAudioBookGen}"; Flags: nowait postinstall skipifsilent
