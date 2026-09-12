using UnrealBuildTool;
public class EchelonEditorTarget : TargetRules {
 public EchelonEditorTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Editor;
  DefaultBuildSettings = BuildSettingsVersion.V5;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
  ExtraModuleNames.Add("Echelon");
 }
}
