## Date: [2026-01-06]

### 1. Task Description
* Objective: [building data set of myself, ready for later use and demo test/debug]
* Scope: [Unfortuanly lost my NFC test card and I only had one, bought some new ones and they're on the way, so looking foward to interaction designing]

### 2. Implementation Status
* Progress: [not muvh, watting for my device, just foing pepreation:building git connection(github to vscode), db building]
* Blockers: [my NFC card LOST!]

### PS
* TBH this have been starting from last year DEC, anyways, forgot to build a github repository at the time, and my git push update failed for several time. So I'll be catching up when I got my enviorment.

## Date: [2026-01-12]

### 1. Task Description
* Objective: Finalize hardware-to-software bridge and map student UID to the local database.
* Scope: Environment alignment, driver troubleshooting, and initial data capture.

### 2. Implementation Status
* Progress: 
    * Captured Test NFC UID: `1D 69 BC A4 19 10 80`.
    * Localized environment via `.venv` on D: drive to fix pathing conflicts.
    * Resolved hardware error `0x8010001D` by starting the Windows Smart Card service.
    * Cleaned up Git repo using `.gitignore` to exclude environment files.
* Blockers: None. System is ready for logic development.

### PS
* Big win today—hardware is finally talking to the code. After planning this since last December, seeing that UID pop up in the terminal makes the environment troubleshooting worth it. Next up: Public web integration. I also found myself learning a lot, building venv, using gitignore developing and disscusing with AI had help me push through and learn a lot./happy new year btw(mayb a bit too late)

## Date: [2026-01-18]

### 1. Hardware/pre-planning and product shopping plan for taking project to land
* Status: Were now on dev of demo, cause this is the project for the school, I want to show how it works first. But also, to get one step ahead, need to plan for how to take project down
* logic:
    * use an arduino to replace my laptop
    * since I already have an NFC dectactor, find a way to make connection bettwen arduino/dectactor
    * Anti-risk plan:
        * if something went wrong, also having another dectactor which can be directly pluged into arduino is helpful
* result/list:
    * arduino uno r4 wifi: have wifi function/reliable
    * USB Host shield piece: Connect my NFC omnikey to arduino
    * PN532 NFC: as a risk backup option in case any thing broke out
* Developing DEMO will continue when I have time, I'm still back in China right know so I guess I'll need to buy product I need first since it's cheaper in china