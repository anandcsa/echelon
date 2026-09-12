using UnrealBuildTool;
public class EchelonTarget : TargetRules {
 public EchelonTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Game;
  DefaultBuildSettings = BuildSettingsVersion.V5;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
  ExtraModuleNames.Add("Echelon");
  if (Target.Platform == UnrealTargetPlatform.Win64)
   PreBuildSteps.Add("powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$(ProjectDir)Build\\PrepareAssets.ps1\" -EngineDir \"$(EngineDir)\" -ProjectDir \"$(ProjectDir)\"");
 }
}
