<p align="center">
<img width="212" src="https://github.com/EngineersNeedArt/SystemSix/blob/7c597d6baabd1c8c9afefa4abe081f167396a7cb/images/SystemSixLogo.png" alt="SystemSix">
</p>
SystemSix is an e-Ink "desk accessory" running on a Raspberry Pi. It is a bit of nostalgia that can function as a calendar, display the weather, the current phase of the moon or just be generally fun to look at.

To be clear, despite how it looks, it is not interactive. It changes every day to display a new "desktop", will update to show local weather, your calendar events, phase of the moon. But you cannot click on it.

It was wrtitten as a love-letter to my first Macintosh. Hopefully it is nostaglic, somewhat informative, and fun.

<p align="center">
<img src="https://github.com/EngineersNeedArt/SystemSix/blob/10f2332b5c11dc4a585dd9fe9dbc258d303cf0ba/documentation/DisplaySample.png" alt="SystemSix screenshot.">
</p>

### Features

• Calendar date is displayed.

• Retrieves and displays your first six calendar events for the day, refreshes in the evening.

• Retrieves and displays the local weather forecast at the start of each day.

• Current phase of the moon displayed. (New moon? Maybe you get a Calculator instead.)

• Specify "trash day" and on that day of the week, the trash can icon will display full. Can be a handy reminder.

• Several different overall layouts and a random selection from over 100 classic icons means you wake up to a surprise desktop every day.

<p align="center">
<img width="768" src="https://github.com/EngineersNeedArt/SystemSix/blob/cb6224a06ff2554a2e81abf078a4b30b270a5670/documentation/SystemSixDisplayed.jpeg" alt="SystemSix">
</p>

The display is [5.83" e-ink display](https://www.waveshare.com/5.83inch-e-paper.htm) from [Waveshare](https://www.waveshare.com).
   
More (exhaustive) details on how SystemSix was created are [on my blog](https://www.engineersneedart.com/systemsix/systemsix.html).


### Running

If you are new to Python as I was: briefly, you pull down the sources and open `systemsix.py` in a Python IDE (example: Thonny, that generally comes pre-installed on the Raspberry Pi — on a desktop OS, PyCharm is a popular one). Then you *run* it.

Hopefully the `requirements.txt` file covers the needed Python modules and you have no problems running SystemSix. (Hopefully too your Python environment already is pointing to Python3 and not an older Python implmentation.)

In `systemsix.py`, there is a flag at the top: `USE_EINK_DISPLAY`. Set this to `False` and you can run `systemsix.py` in any environment, even without an e-ink display attached. The workflow for updating the e-ink display involves first creating the image that you want displayed. Most of the code in SystemSix is doing just that: creating the final image of the desktop. When you set `USE_EINK_DISPLAY` to `False` the final image is instead opened in your current OS environment, not sent to the e-ink driver. (On MacOS it is Preview that is launched to display the resulting image.)

See the *Settings* section below on how to customize SystemSix and personalize it.

To dedicate a Raspberry Pi to run SystemSix headless, I had to learn about `crontab`. This is the program that is run to schedule automatic tasks on the computer. Once set up, it requires no human interaction.

In the Terminal app on a Raspberry Pi I entered:

`crontab -e`

This brings up a text editor in Terminal. Then I scrolled down to the bottom of the file and added this line:

`@reboot sleep 60 && /home/pi/SystemSix/run_systemsix.sh`

This says that 60 seconds after booting, the computer will run the shell script named `run_systemsix.sh` located at the path `/home/pi/SystemSix/`. If you pulled the files down somewhere else you will have a different path to the shell script file.

### Settings

"Trash day" is defined in `settings.py` as an integer. Set the value to `1` for Monday, `2` for Tuesday, etc. Setting the value to `None` will cause the trash to never be shown full. Set to any other value to indicate that "trash day" should be random.

For the weather API I use, `LATITUDE` and `LONGITUDE` should be supplied in `settings.py`. I query [api.weather.gov](api.weather.gov) to turn the LAT/LONG into an office ID and grid X and Y that weather.gov uses to retrieve local forecasts.

To display your upcoming calendar events the settings and code are the same as the implementation from 13Bytes. I can only speak to my experiences with MacOS Calendar. `WEBDAV_IS_APPLE` I set to `True` and for `WEBDAV_CALENDAR_URL` I entered the URL to fetch my public calendar.

Figuring out my calendar URL turned out to be a challenge. In the end I had to create a new calendar in Apple's Calendar app and make sure to mark it as *public*. Then I found the sharing affordance in Calendar and "shared" the calendar with myself (I emailed it to myself). The link in the email contained the (150+ character) URL that I was then able to paste into `settings.py`. Mine started out like this: `webcal://p97-caldav.icloud.com/published/2/NDYyNT....`.

### Technical

E-ink displays, at least the hobbyist-priced ones (or maybe it's their drivers), are both slow and a little unsightly when they refresh. I had wanted to play with them however so chose a project (a calendar/weather app) where infrequent display refreshes were acceptable.

I'm new to both Python and e-ink displays, so forgive me if my explanation here is a little off. As I touched on earlier, I found that the general gist of displaying content to the e-ink display was to build an image of the correct width/height and in the correct bit depth for the display using the graphics library of your choice (PIL or "Pillow" for Python) and then call the e-ink driver code to display that finished image.

There is then a whole bunch of flashing and flickering of the e-ink display that goes on until, some dozen seconds or so later, your image is visible. It is, I find, quite distracting. To that end, the code tries to minimize the refreshes, updates.

At midnight the display gets a refresh. Since the current calendar date is one of the things we display, updating at midnight is a no-brainer. The display is updated.

Morning (currently I have chosen 4:05 AM) gets a special update. It is this update/period when a new layout/desktop is chosen for the day. There will of course always be a display update/refresh in the morning. Further, it is the morning period when both the weather forecast and calendar events are first attempted.

The weather API I am using often fails. Or rather, it often returns a bogus forecast. It's not that the forecast is inaccurate, instead it is a forecast from several months past. I added code to test a date in the forecast that is returned and reject these errant forecasts. Additionally, I note that fetching the weather failed.

Every hour the app awakens and decides whether to update or not. If it had failed to fetch the weather (or calendar events) the previous hour it will kick off another fetch. Only if it succeeds then will it refresh the display. If it fails again it goes back to sleep and will retry an hour later.

An hour between updates (especially failed ones) may seem rather coarse but I kind of like that the app is more patient than I am.

The only other special update is the evening update (currently 5:05 PM). Calendar events are again refreshed (to show the next day's events) and the desktop is refreshed. It is with the evening refresh that the desktop code may display the phase of the moon by bringing up the Moon "desk accessory".

If all the fetches are happy, you are likely never to actually see the display update except perhaps the evening update.

### Esoterica

Inspired of course by the early Macintosh (my first Apple computer was a Macintosh Plus, and I loved it). The display is not precisely 512 × 342 pixels as were the early "classic" Macs. There is no e-Ink display of this resolution. The 5.83" E-Ink display from Waveshare was close at 648 × 480.

Pixels on the e-ink display are right up to the edge where the metal of the panel meets. I found that if I presented content right up to the edges I could not easily attach a plastic bezel that would hide the metal trim of the panel without obscuring some of the pixels. For that reason I intentionally left a "letterbox", black padding pixels (or a matte if you prefer) on all four sides of the content.

Had I left about 68 pixels of black border all around I could have displayed the content precisely at 512 × 342. I feel the panel is already small and I did not want to shrink the content by that degree. This is a compromise.

This project was my introduction to learning Python. I started from the sources of the beautiful [eInkCalendar](https://github.com/13Bytes/eInkCalendar) submitted by [13Bytes](https://github.com/13Bytes). I did a lot of refactoring of 13Bytes code and added a lot of rendering code to display the desktop and icons in various configurations. I added the weather and phases of the Moon. Much of the effort though involved preparing image assets, coming up with visually attractive desktop layouts.

In fact the idea for SystemSix came about when I went to add phases of the Moon to 13Bytes' original eInkCalendar. To display the moon in black and white I decided to dither the grayscale source art. [Atkinson dithering](https://en.wikipedia.org/wiki/Dither) was a nice algorithm I remember from the classic Mac days and so I sought that out. Once I saw the moon "Atkinson dithered" on an e-ink display my thoughts for the project went in a whole different direction — and so SystemSix came about.

### Issues

The weather API, api.weather.gov is not real reliable in my area. For reasons I don't understand the forecast returned is often, errantly, a forecast from the end of December 2021. It's an odd bug, I know. Nonetheless, I added (BOGUS) code to look for this incorrect forecast and reject it. I designed  the code though to re-try failed data fetches every hour. Often when I get the bogus weather forecast it will eventually come back correct some hours later.

I could move to a different weather API, but from having just dipped my toe into web API, it looked like most API require the user to set up an account and then pass a token in the query URL. That seemed pretty user-unfriendly, more hoops to go through to get SystemSix up and running. So for now I passed on looking further into it.

The fonts are not all perfect. Many are missing fairly common glyphs (I had to manually edit the Geneva 9 font to add the *degree* glyph, for example). Kerning, spacing might not be ideal (the space character in Geneva 9 was way too wide and I had to go in and tighten it up).

I cheated to get a bold "Geneva 12" and just rendered the font twice; offset to the right by one pixel on the second render.

Because the display is ultimately two values (B&W) any sort of aliasing will look bad when displayed. Careful attention therefore has to be made to find the precise font size that will yield glyphs on perfect pixel boundaries.

### Acknowledgments

Code base began from [eInkCalendar](https://github.com/13Bytes/eInkCalendar) by 13Bytes.

The [ChiKareGo2](http://www.suppertime.co.uk/blogmywiki/2017/04/chicago/) font is under Creative Commons license.

The artwork came from taking screenshots of the excellent [MiniVMac](https://www.gryphel.com/c/minivmac/) emulator.

<p align="center">
<i>"Good enough for 1.0…"</i>
</p>
