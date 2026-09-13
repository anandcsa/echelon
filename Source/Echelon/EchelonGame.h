#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "EchelonGame.generated.h"

class UCapsuleComponent;
class UBoxComponent;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UPixelStreamingInput;

UCLASS()
class ECHELON_API AEchelonController : public APlayerController
{
    GENERATED_BODY()
  public:
    AEchelonController();
    virtual void BeginPlay() override;
    UFUNCTION() void ForwardBrowserMessage(const FString &Descriptor);

  private:
    UPROPERTY() UPixelStreamingInput *BrowserInput;
};

UCLASS()
class ECHELON_API AEchelonWalker : public APawn
{
    GENERATED_BODY()
  public:
    AEchelonWalker();
    virtual void Tick(float Dt) override;
    virtual void SetupPlayerInputComponent(UInputComponent *Input) override;
    void Forward(float V);
    void Right(float V);
    void Turn(float V);
    void Look(float V);
    void Interact();
    void Pause();

  private:
    UPROPERTY() UCapsuleComponent *Body;
    UPROPERTY() UCameraComponent *Camera;
    float ForwardAxis = 0, RightAxis = 0;
};

UCLASS()
class ECHELON_API AEchelonCar : public APawn
{
    GENERATED_BODY()
  public:
    AEchelonCar();
    virtual void Tick(float Dt) override;
    virtual void SetupPlayerInputComponent(UInputComponent *Input) override;
    void Forward(float V);
    void Right(float V);
    void BrakeDown();
    void BrakeUp();
    void Interact();
    void Pause();
    float Speed = 0;

  private:
    UPROPERTY() UBoxComponent *Body;
    UPROPERTY() UStaticMeshComponent *Mesh;
    UPROPERTY() USpringArmComponent *Arm;
    UPROPERTY() UCameraComponent *Camera;
    float Throttle = 0, Steer = 0;
    bool Braking = false;
};

UCLASS()
class ECHELON_API AEchelonMara : public AActor
{
    GENERATED_BODY()
  public:
    AEchelonMara();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    bool Following = false;

  private:
    UPROPERTY() UCapsuleComponent *Body;
    UPROPERTY() UStaticMeshComponent *Mesh;
    FVector Home;
    float Time = 0;
};

UCLASS()
class ECHELON_API AEchelonGameMode : public AGameModeBase
{
    GENERATED_BODY()
  public:
    AEchelonGameMode();
    virtual void StartPlay() override;
    virtual void Tick(float Dt) override;
    void Interact();
    void AskMara(const FString &Question);
    void SaveCheckpoint();
    UFUNCTION() void OnBrowserMessage(const FString &Descriptor);
    static bool InsideCity(const FVector &Position);
    FString Speech = TEXT("Mara: The city remembers the version of you it prefers. Find me by the avenue.");
    FString Connection = TEXT("LOCAL FALLBACK");
    bool Busy = false;
    float ExternalForward = 0, ExternalRight = 0, ExternalUntil = 0;
    bool ExternalBrake = false;
    UPROPERTY() AEchelonCar *Car;
    UPROPERTY() AEchelonWalker *Walker;
    UPROPERTY() AEchelonMara *Mara;

  private:
    UPROPERTY() UPixelStreamingInput *StreamInput;
    FString Session;
    TArray<FString> Memory;
    float NextThink = 15, NextSave = 25;
    void SendBrowser(const FString &Kind, const FString &Text);
};

UCLASS()
class ECHELON_API AEchelonHUD : public AHUD
{
    GENERATED_BODY()
  public:
    virtual void DrawHUD() override;
    virtual void NotifyHitBoxClick(FName BoxName) override;
};
