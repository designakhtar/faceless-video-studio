# Faceless Video Studio

## How to use it
Open Claude Code in this folder and say something like:
- "Make a 5-minute video about why we dream"
- "Make a video from this email: ..." (or "from the email from Sam about the launch")
- "Make a video like this reference: <file>"

Claude writes the script and stops. Reply **OK** (or ask for changes).
Next Claude shows the shot plan and **the credit cost**, then waits for a second **OK** before spending anything.
After that it does the rest and gives you `final/<name>.mp4` plus a short report.

## What's free and what costs money
| Part | Tool | Cost |
|---|---|---|
| Script, storyboard, prompts | Claude | included in your Claude plan |
| Voiceover | Kokoro (runs locally) | free |
| Captions | Whisper (runs locally) | free |
| Background music | MusicGen-small (runs locally) | free |
| Titles / graphics | HyperFrames (Apache-2.0) | free |
| Titles / graphics | Remotion | free for individuals and companies with 3 or fewer people. Bigger companies need a paid licence |
| Editing / final MP4 | FFmpeg | free |
| **3D video shots** | Google Flow (Veo 3.1) | uses your **Google AI Pro** monthly Flow credits: about 10 per 8-second clip on "Lite" (about 380 for a 5-minute video). These are estimates |
| **3D video shots** (backup) | Higgsfield | **paid credits**: about 8 to 56 per clip depending on the model. Your free plan has 6.2 credits, which is not enough for even one clip on most models |

## Google Flow login (the one step only you can do)
The Google Flow connection drives a real Chrome window that is signed in to *your* Google account.
1. In that Chrome window, sign in to your Google account (the one with Google AI Pro).
2. Go to labs.google/fx/tools/flow and click **"Sign in to Flow"** once.
That's it. The login is saved and reused.

**Where this has to run:** this login needs a Chrome window you can see and click, so it has to run on **your own computer**.
It can't run in this cloud workspace. Two options:
- **Easiest:** connect your computer to Claude (Claude desktop app → Settings → Claude Code → Remote Control, then share a folder). Then tell Claude "install the studio on my computer" and it does the setup there.
- **Or:** use Higgsfield for the shots (it works from the cloud, but it costs paid credits).

## ⚠️ Terms-of-service warning (please read)
The Google Flow connector is **unofficial**. Google has no public API for Flow.
It controls Chrome automatically and deliberately hides that it's automated.
Automating Google services this way **can break Google's Terms of Service**. That could get your Google account limited or suspended.
Use it only on an account you can afford to risk, at a slow pace (one clip at a time).
The safer alternatives are official paid APIs (Higgsfield, or Google's own Gemini/Vertex API for Veo).

## Folders
`scripts` approved scripts · `storyboards` shot lists and prompts · `characters` your fixed character sheet ·
`shots` video clips · `graphics` titles and overlays · `audio` voice, captions, music · `final` finished videos + reports.
`tools/`, `templates/`, `.tools/` are the engine. After cloning on a new computer run `bash setup.sh` once to reinstall the large parts (`.venv`, `node_modules`).
