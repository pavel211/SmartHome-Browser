#define MyAppName "Smart Home Browser"
#define MyAppVersion "1.0"
#define AppExe "SmartHomeBrowser.exe"
#define LauncherExe "ShowBrowser.exe"

[Setup]
AppId={{8F3A1C2D-9B11-4E2A-8C7D-11AA22BB33CC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\SmartHomeBrowser
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=SmartHomeBrowserSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist/SmartHomeBrowser.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist/ShowBrowser.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Главное приложение
Name: "{group}\Smart Home Browser"; Filename: "{app}\{#AppExe}"; IconFilename: "{app}\icon.ico"

; Launcher
Name: "{group}\Show Browser Control"; Filename: "{app}\{#LauncherExe}"; IconFilename: "{app}\icon.ico"

[Registry]
; Автозагрузка SmartHomeBrowser.exe
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
ValueType: string; ValueName: "SmartHomeBrowser"; \
ValueData: """{app}\{#AppExe}"""; Flags: uninsdeletevalue

[Run]
; Запуск после установки
Filename: "{app}\{#AppExe}"; Description: "Запуск Smart Home Browser"; Flags: nowait postinstall skipifsilent