using UnrealBuildTool;
public class Echelon : ModuleRules {
 public Echelon(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new [] {"Core", "CoreUObject", "Engine", "InputCore", "HTTP", "Json", "JsonUtilities", "PixelStreaming"});
 }
}
