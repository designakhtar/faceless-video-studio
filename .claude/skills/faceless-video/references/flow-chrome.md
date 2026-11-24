# Google Flow through Claude in Chrome

Load the chrome-browser skill if listed. Use the user's Chrome, a new tab, https://flow.google.com/.

1. Check it is signed in (PRO badge). Account icon = credit balance. **Then reload the page**: while that panel is
   open, typed text becomes keyboard shortcuts (it once switched on a filter and the Agent).
2. Open the video's project, or New project. Keep its URL.
3. Flow Agent must be OFF (the prompt box says "What do you want to create?").
4. Open the settings button: Video, Ingredients, 16:9, Veo 3.1 - Lite, **x1** (default was x2 = double cost).
   Read "Generating will use N credits". If it differs from what the user approved, stop and ask.
   Veo 3.1 Lite fixed the length to 8 s. Models and prices change, so trust the page.
5. Use `find` and click by ref, not coordinates: the window size can change mid-session.
6. Click the prompt box, Ctrl+A, type the prompt as ONE line, screenshot, check its start and end and that it shows
   720p 8s x1. Only then click Start generation, once. The old prompt stays in the box afterwards.
   Never click again because a tile looks slow; a clip takes about a minute.
7. Two or three clips may run at once. Send the next only after the previous tile appears.
8. Download: open the tile, download icon, **720p Original size**. Files land in Downloads under Flow's own title.
   Note which title belongs to which shot, then use `studio.py import`.
9. Confirm the balance at the end, then close your tab.

Failed tile: check whether credits were refunded and ask before retrying.
CAPTCHA, unusual-activity notice or terms to accept: stop and tell the user.
