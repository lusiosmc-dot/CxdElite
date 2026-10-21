#!/usr/bin/env python3
"""CxdElite Launcher branding script (run from repo root: python3 apply_branding.py).
Needs: pip install pillow"""
import os, re

# ---- switches: set False to skip a phase if the build fails ----
PHASE_GLASS_DEFAULTS = True   # Phase 1: blur/opacity defaults + glass cards
PHASE_WALLPAPER      = True   # Phase 2: default wallpaper from logo.png on first run
PHASE_SHAPES         = True   # Phase 3-5: rounded glass shapes on ALL screens/dialogs/buttons
PHASE_HOME           = True   # Home: remove test warning card, fix top bar name
PHASE_PORTRAIT       = True   # Launcher in portrait mode (game itself stays landscape)
PHASE_PORTRAIT_FIT   = True   # Portrait: give landscape-designed screens more room + top gap
PHASE_WIDE_CARD      = True   # Version card on home = full width (resets saved home layout once)
PORTRAIT_DEFAULT     = False  # True = launcher starts in portrait, False = starts in landscape (rotate button works either way)
PHASE_ROTATE_BUTTON  = True   # Rotate button in the top bar (remembers your choice)
PHASE_SPLASH_GLASS   = True   # Wallpaper + glass on the first-run extract screen
PHASE_MODRINTH       = True   # Default download platform = Modrinth
PORTRAIT_SCALE       = 0.70   # smaller = more room (layout), 1.0 = normal. Try 0.6 to 0.8
PORTRAIT_TEXT        = 0.95   # text size in portrait relative to normal
PORTRAIT_TOP_GAP     = 28     # dp gap at the top of portrait screens
R = "ZalithLauncher/src/main/res"
M = "ZalithLauncher/src/main"

def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        s = re.sub(a, b, s)
    open(path, "w", encoding="utf-8").write(s)

# ---- names ----
sub("ZalithLauncher/gradle.properties", [
    (r"(?m)^launcher_name=.*", "launcher_name=CxdEliteLauncher"),
    (r"(?m)^launcher_app_name=.*", "launcher_app_name=CxdElite Launcher"),
    (r"(?m)^launcher_short_name=.*", "launcher_short_name=CxdE"),
])
sub("ZalithLauncher/build.gradle.kts", [
    (r"applicationId = zalithPackageName", 'applicationId = "com.cxdelite.launcher"'),
    (r'\n\s*applicationIdSuffix = "\.v2"', ""),
])
for p in (M + "/AndroidManifest.xml", R + "/values/themes.xml", R + "/values-night/themes.xml"):
    sub(p, [(r"AppTheme\.ZalithLauncher", "AppTheme.CxdEliteLauncher")])
sub(R + "/values-pt-rBR/strings.xml", [(r"ZalithLauncher2", "CxdElite Launcher")])
sub(M + "/java/com/movtery/zalithlauncher/ui/activities/VMActivity.kt",
    [(r"ZalithLauncher: Direct gamepad", "CxdEliteLauncher: Direct gamepad")])
open("NOTICE.md", "w").write("""# CxdElite Launcher

CxdElite Launcher is a rebranded fork of Zalith Launcher 2
(https://github.com/ZalithLauncher/ZalithLauncher2) by MovTery and contributors.

Licensed under GPL-3.0 (see LICENSE). All original copyright notices are retained.
Source code must remain publicly available under the same license.
""")

# ---- Phase 1: glass theme (defaults + card look) ----
K = M + "/java/com/movtery/zalithlauncher"
def patch(path, pairs):
    t = open(path, encoding="utf-8").read()
    for a, b, n in pairs:
        assert t.count(a) == n, f"{path}: expected {n} of {a!r}, found {t.count(a)}"
        t = t.replace(a, b)
    open(path, "w", encoding="utf-8").write(t)

if PHASE_GLASS_DEFAULTS:
    patch(K + "/setting/AllSettings.kt", [
        ('intSetting("launcherBackgroundOpacity", 80, 20..100)', 'intSetting("launcherBackgroundOpacity", 55, 20..100)', 1),
        ('intSetting("backgroundBlur", 0, 0..40)', 'intSetting("backgroundBlur", 24, 0..40)', 1),
    ])
    patch(K + "/ui/components/BackgroundCard.kt", [
        ("shape: Shape = CardDefaults.shape,", "shape: Shape = RoundedCornerShape(24.dp),", 2),
        ("border: BorderStroke? = null,", "border: BorderStroke? = BorderStroke(1.dp, Color.White.copy(alpha = 0.18f)),", 2),
        ("import androidx.compose.foundation.layout.fillMaxWidth\n",
         "import androidx.compose.foundation.layout.fillMaxWidth\nimport androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.ui.unit.dp\n", 1),
    ])


if PHASE_SHAPES:
    patch(K + "/ui/theme/Theme.kt", [
        ("import androidx.compose.material3.MotionScheme\n",
         "import androidx.compose.material3.MotionScheme\nimport androidx.compose.material3.Shapes\nimport androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.ui.unit.dp\n", 1),
        ("            typography = AppTypography,\n            content = content",
         "            typography = AppTypography,\n            shapes = Shapes(\n                extraSmall = RoundedCornerShape(10.dp),\n                small = RoundedCornerShape(16.dp),\n                medium = RoundedCornerShape(22.dp),\n                large = RoundedCornerShape(28.dp),\n                extraLarge = RoundedCornerShape(36.dp)\n            ),\n            content = content", 1),
    ])

if PHASE_WALLPAPER and os.path.exists("logo.png"):
    from PIL import Image as _I
    os.makedirs(M + "/assets", exist_ok=True)
    _w = _I.open("logo.png").convert("RGB")
    _w.resize((1080, 1080)).save(M + "/assets/cxdelite_bg.jpg", "JPEG", quality=88)
    patch(K + "/ZLApplication.kt", [
        ("            DEVICE_ARCHITECTURE = Architecture.getDeviceArchitecture()\n",
         "            DEVICE_ARCHITECTURE = Architecture.getDeviceArchitecture()\n"
         "            //CxdElite: first-run default glass wallpaper\n"
         "            runCatching {\n"
         "                val bg = PathManager.FILE_LAUNCHER_BACKGROUND\n"
         "                val mark = java.io.File(bg.parentFile, \".cxd_seeded\")\n"
         "                if (!mark.exists()) {\n"
         "                    bg.parentFile?.mkdirs()\n"
         "                    if (!bg.exists()) assets.open(\"cxdelite_bg.jpg\").use { i -> bg.outputStream().use { o -> i.copyTo(o) } }\n"
         "                    mark.createNewFile()\n"
         "                }\n"
         "            }\n", 1),
    ])

if PHASE_HOME:
    patch(K + "/ui/screens/content/home/HomeCards.kt", [
        ("        if (BuildConfig.DEBUG) {\n            add(debugWarningCard())\n        }\n",
         "        //CxdElite: test-version warning removed\n", 1),
    ])
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("text = BuildKeys.LAUNCHER_IDENTIFIER,", "text = BuildKeys.LAUNCHER_NAME,", 1),
    ])

if PHASE_PORTRAIT:
    # launcher screens -> portrait (VMActivity = the game, ControlEditor, ErrorActivity stay landscape)
    if PORTRAIT_DEFAULT:
        patch(M + "/AndroidManifest.xml", [
            ('            android:configChanges="keyboardHidden|orientation|screenSize|smallestScreenSize|screenLayout|keyboard|navigation"\n            android:screenOrientation="sensorLandscape">\n            <intent-filter>',
             '            android:configChanges="keyboardHidden|orientation|screenSize|smallestScreenSize|screenLayout|keyboard|navigation"\n            android:screenOrientation="portrait">\n            <intent-filter>', 1),
            ('            android:name=".ui.activities.MainActivity"\n            android:launchMode="singleTop"\n            android:configChanges="keyboardHidden|orientation|screenSize|smallestScreenSize|screenLayout|keyboard|navigation"\n            android:screenOrientation="sensorLandscape" />',
             '            android:name=".ui.activities.MainActivity"\n            android:launchMode="singleTop"\n            android:configChanges="keyboardHidden|orientation|screenSize|smallestScreenSize|screenLayout|keyboard|navigation"\n            android:screenOrientation="portrait" />', 1),
        ])
    PORTRAIT_HOME = """            if (maxWidth < maxHeight) {
                CompositionLocalProvider(
                    LocalUriHandler provides object : UriHandler {
                        override fun openUri(uri: String) {
                            onOpenLink(uri)
                        }
                    }
                ) {
                    Column(modifier = Modifier.fillMaxSize()) {
                        ContentMenu(
                            modifier = Modifier
                                .weight(1f)
                                .fillMaxWidth(),
                            isVisible = isVisible,
                            onLaunchGame = { version ->
                                onLaunchGame(version)
                            },
                            onQuickPlayServer = onQuickPlayServer,
                            onOpenVersionSettings = navigateToVersions
                        )
                        ActionMenu(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(300.dp)
                                .padding(12.dp),
                            isVisible = isVisible,
                            isTaller = false,
                            dockedSide = dockedSide,
                            onLaunchGame = onLaunchGame,
                            swapTargetValue = 0.dp,
                            pickUpScale = { 1f },
                            toAccountManageScreen = toAccountManageScreen,
                            toVersionManageScreen = toVersionManageScreen,
                            toVersionSettingsScreen = toVersionSettingsScreen
                        )
                    }
                }
            } else {
"""
    patch(K + "/ui/screens/content/LauncherScreen.kt", [
        ("import androidx.compose.foundation.layout.Row\n",
         "import androidx.compose.foundation.layout.Row\nimport androidx.compose.foundation.layout.fillMaxWidth\nimport androidx.compose.foundation.layout.height\nimport androidx.compose.foundation.layout.padding\n", 1),
        ("            // 内容区域\n            Row(modifier = Modifier.fillMaxSize()) {",
         PORTRAIT_HOME + "            // 内容区域\n            Row(modifier = Modifier.fillMaxSize()) {", 1),
        ("                        toVersionSettingsScreen = toVersionSettingsScreen\n                    )\n                }\n            }\n        }\n    }\n}\n",
         "                        toVersionSettingsScreen = toVersionSettingsScreen\n                    )\n                }\n            }\n            }\n        }\n    }\n}\n", 1),
    ])

if PHASE_PORTRAIT_FIT:
    patch(K + "/ui/theme/Theme.kt", [
        ("            content = content\n        )\n",
         "            content = { PortraitFit(content) }\n        )\n", 1),
    ])
    with open(K + "/ui/theme/Theme.kt", "a", encoding="utf-8") as _f:
        _f.write(f"""

/** CxdElite: in portrait, lay screens out on a wider virtual canvas (they were designed for landscape) */
@androidx.compose.runtime.Composable
private fun PortraitFit(content: @androidx.compose.runtime.Composable () -> Unit) {{
    val cfg = androidx.compose.ui.platform.LocalConfiguration.current
    val d = androidx.compose.ui.platform.LocalDensity.current
    if (cfg.orientation == android.content.res.Configuration.ORIENTATION_PORTRAIT) {{
        androidx.compose.runtime.CompositionLocalProvider(
            androidx.compose.ui.platform.LocalDensity provides androidx.compose.ui.unit.Density(
                density = d.density * {PORTRAIT_SCALE}f,
                fontScale = d.fontScale * ({PORTRAIT_TEXT}f / {PORTRAIT_SCALE}f)
            )
        ) {{ content() }}
    }} else {{
        content()
    }}
}}
""")
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("import androidx.compose.ui.unit.dp\n",
         "import androidx.compose.ui.unit.dp\nimport androidx.compose.foundation.layout.padding\n", 1),
        ("        Column(\n            modifier = Modifier\n                .fillMaxSize()\n        ) {\n            TopBar(",
         "        Column(\n            modifier = Modifier\n                .fillMaxSize()\n"
         f"                .padding(top = if (androidx.compose.ui.platform.LocalConfiguration.current.orientation == android.content.res.Configuration.ORIENTATION_PORTRAIT) {PORTRAIT_TOP_GAP}.dp else 0.dp)\n"
         "        ) {\n            TopBar(", 1),
    ])

if PHASE_WIDE_CARD:
    patch(K + "/ui/screens/content/home/HomeCards.kt", [
        ("    private val versionCardType = CardType(\n        typeId = VERSION_CARD_TYPE_ID,\n        defaultSpan = IntOffset(10, 6),",
         "    private val versionCardType = CardType(\n        typeId = VERSION_CARD_TYPE_ID,\n        defaultSpan = IntOffset(1000, 6), //CxdElite: 1000 = clamped to the full grid width", 1),
    ])
    # new storage key -> old small saved layout is ignored, cards are re-added full width
    patch(K + "/ui/screens/content/home/HomeGridPersistence.kt", [
        ('private const val KEY_LAYOUT = "homeCardLayout"', 'private const val KEY_LAYOUT = "homeCardLayoutCxd1"', 1),
    ])

if PHASE_ROTATE_BUTTON:
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("                IconButton(\n                    onClick = openFileManager\n                ) {",
         """                val cxdCtx = androidx.compose.ui.platform.LocalContext.current
                IconButton(
                    onClick = {
                        var c: android.content.Context = cxdCtx
                        while (c is android.content.ContextWrapper && c !is android.app.Activity) c = c.baseContext
                        (c as? android.app.Activity)?.let { a ->
                            val toPortrait = a.resources.configuration.orientation != android.content.res.Configuration.ORIENTATION_PORTRAIT
                            a.requestedOrientation = if (toPortrait) android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                                else android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
                            a.getSharedPreferences("cxd", 0).edit().putBoolean("portrait", toPortrait).apply()
                        }
                    }
                ) {
                    Icon(
                        painter = painterResource(R.drawable.ic_mobile_rotate_filled),
                        contentDescription = null
                    )
                }

                IconButton(
                    onClick = openFileManager
                ) {""", 1),
    ])
    patch(K + "/ui/activities/MainActivity.kt", [
        ("        super.onCreate(savedInstanceState)\n        //处理外部导入",
         "        super.onCreate(savedInstanceState)\n"
         "        //CxdElite: restore the rotate-button choice\n"
         "        if (getSharedPreferences(\"cxd\", 0).getBoolean(\"portrait\", PORTRAIT_FLAG)) {\n"
         "            requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT\n"
         "        } else {\n"
         "            requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE\n"
         "        }\n"
         "        //处理外部导入".replace("PORTRAIT_FLAG", "true" if PORTRAIT_DEFAULT else "false"), 1),
    ])

if PHASE_SPLASH_GLASS:
    patch(K + "/ui/activities/SplashActivity.kt", [
        ("    private val backStackViewModel: SplashBackStackViewModel by viewModels()\n",
         "    private val backStackViewModel: SplashBackStackViewModel by viewModels()\n"
         "    private val backgroundViewModel: com.movtery.zalithlauncher.viewmodel.BackgroundViewModel by viewModels()\n", 1),
        ("            ZalithLauncherTheme {\n                Surface(\n                    modifier = Modifier.fillMaxSize(),\n                    color = backgroundColor(),",
         "            ZalithLauncherTheme(backgroundViewModel = backgroundViewModel) {\n"
         "                androidx.compose.foundation.layout.Box(Modifier.fillMaxSize()) {\n"
         "                com.movtery.zalithlauncher.ui.screens.content.elements.Background(\n"
         "                    modifier = Modifier.fillMaxSize(),\n"
         "                    viewModel = backgroundViewModel\n"
         "                )\n"
         "                Surface(\n                    modifier = Modifier.fillMaxSize(),\n                    color = androidx.compose.ui.graphics.Color.Transparent,", 1),
        ("                        screenViewModel = backStackViewModel\n                    )\n                }\n",
         "                        screenViewModel = backStackViewModel\n                    )\n                }\n                }\n", 1),
    ])

if PHASE_MODRINTH:
    patch(K + "/setting/AllSettings.kt", [
        ('enumSetting("searchModPlatform", Platform.CURSEFORGE)', 'enumSetting("searchModPlatform", Platform.MODRINTH)', 1),
        ('enumSetting("searchModpackPlatform", Platform.CURSEFORGE)', 'enumSetting("searchModpackPlatform", Platform.MODRINTH)', 1),
        ('enumSetting("searchResourcePackPlatform", Platform.CURSEFORGE)', 'enumSetting("searchResourcePackPlatform", Platform.MODRINTH)', 1),
        ('enumSetting("searchShadersPlatform", Platform.CURSEFORGE)', 'enumSetting("searchShadersPlatform", Platform.MODRINTH)', 1),
    ])
    patch(K + "/ui/screens/content/download/assets/search/SearchIdScreen.kt", [
        ("var platform by mutableStateOf(Platform.CURSEFORGE)", "var platform by mutableStateOf(Platform.MODRINTH)", 1),
    ])

# ---- logo ----
from PIL import Image, ImageDraw, ImageChops
import math, sys
SS=4
def hexpts(cx,cy,r):
    return [(cx+r*math.sin(math.radians(60*i)), cy-r*math.cos(math.radians(60*i))) for i in range(6)]
def grad(size,c1,c2):
    g=Image.new("RGBA",(size,size))
    px=g.load()
    for y in range(size):
        for x in range(size):
            t=(x+y)/(2*size-2)
            px[x,y]=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))+(255,)
    return g
def letters(d,cx,cy,s,fill):
    # "C" ring + "E" bars, total width ~ 1.9*s
    th=s*0.26
    # C
    ccx=cx-s*0.55; r=s*0.62
    d.arc([ccx-r,cy-r,ccx+r,cy+r],40,320,fill=fill,width=int(th))
    # round caps
    for a in (40,320):
        ex=ccx+(r-th/2)*math.cos(math.radians(a)); ey=cy+(r-th/2)*math.sin(math.radians(a))
        d.ellipse([ex-th/2,ey-th/2,ex+th/2,ey+th/2],fill=fill)
    # E
    ex0=cx+s*0.30; w=s*0.78; h=r*2
    d.rectangle([ex0,cy-r,ex0+th,cy+r],fill=fill)
    for yy in (cy-r, cy-th/2, cy+r-th):
        d.rectangle([ex0,yy,ex0+w,yy+th],fill=fill)
def render(size, mode, scale=1.0):
    """mode: icon (bg+logo), fg (transparent, logo only), mono (white silhouette), logo (transparent big)"""
    S=size*SS
    img=Image.new("RGBA",(S,S),(0,0,0,0))
    if mode=="icon":
        ImageDraw.Draw(img).rectangle([0,0,S,S],fill=(11,16,32,255))
    elif mode=="round":
        ImageDraw.Draw(img).ellipse([0,0,S-1,S-1],fill=(11,16,32,255))
    cx=cy=S/2; R=S*0.34*scale
    mask=Image.new("L",(S,S),0)
    md=ImageDraw.Draw(mask)
    md.polygon(hexpts(cx,cy,R),fill=255)
    if mode=="mono":
        hexl=Image.new("RGBA",(S,S),(255,255,255,255))
        img.paste(hexl,(0,0),mask)
        cut=Image.new("L",(S,S),0); letters(ImageDraw.Draw(cut),cx,cy,R*0.55,255)
        a=img.split()[3]; a=ImageChops.subtract(a,cut); img.putalpha(a)
    else:
        img.paste(grad(S,(0,229,255),(124,77,255)),(0,0),mask)
        # inner dark hex ring for depth
        inner=Image.new("L",(S,S),0)
        ImageDraw.Draw(inner).polygon(hexpts(cx,cy,R*0.86),fill=255)
        dark=Image.new("RGBA",(S,S),(11,16,32,255))
        img.paste(dark,(0,0),inner)
        ImageDraw.Draw(img).line(hexpts(cx,cy,R*0.86)+[hexpts(cx,cy,R*0.86)[0]],fill=(255,255,255,0),width=1)
        letters(ImageDraw.Draw(img),cx,cy,R*0.50,(255,255,255,255))
    return img.resize((size,size),Image.LANCZOS)

from PIL import ImageFilter
os.makedirs(R + "/drawable-nodpi", exist_ok=True)
SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

def circle(im):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, im.size[0]-1, im.size[1]-1], fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

def rounded(im, rad):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0]-1, im.size[1]-1], rad, fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

if os.path.exists("logo.png"):
    src = Image.open("logo.png").convert("RGB")
    side = min(src.size)
    src = src.crop(((src.width-side)//2, (src.height-side)//2, (src.width+side)//2, (src.height+side)//2))
    for d, s in SIZES.items():
        src.resize((s, s), Image.LANCZOS).save(f"{R}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=95)
        circle(src.resize((s*4, s*4), Image.LANCZOS)).resize((s, s), Image.LANCZOS).save(f"{R}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=95)
    # adaptive icon: blurred backdrop + full logo inside the safe zone
    C = 648
    bg = src.resize((C, C), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg.save(R + "/drawable-nodpi/ic_launcher_bg.png")
    fg = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    inner = rounded(src.resize((436, 436), Image.LANCZOS), 40)
    fg.paste(inner, ((C-436)//2, (C-436)//2), inner)
    fg.save(R + "/drawable-nodpi/ic_launcher_foreground.png")
    for f in ("ic_launcher.xml", "ic_launcher_round.xml"):
        open(f"{R}/mipmap-anydpi-v26/{f}", "w").write(
            '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@drawable/ic_launcher_bg"/>\n'
            '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n</adaptive-icon>\n')
    for f in ("ic_launcher_foreground.xml", "ic_launcher_monochrome.xml"):
        if os.path.exists(f"{R}/drawable/{f}"):
            os.remove(f"{R}/drawable/{f}")
    rounded(src.resize((1024, 1024), Image.LANCZOS), 120).save(R + "/drawable/img_launcher.png")
    print("Custom logo.png applied.")
else:
    for d, s in SIZES.items():
        render(s*2, "icon", 1.15).resize((s, s)).save(f"{R}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=95)
        render(s*2, "round", 1.0).resize((s, s)).save(f"{R}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=95)
    render(648, "fg", 1.0).save(R + "/drawable-nodpi/ic_launcher_foreground.png")
    render(648, "mono", 1.0).save(R + "/drawable-nodpi/ic_launcher_monochrome.png")
    for f in ("ic_launcher_foreground.xml", "ic_launcher_monochrome.xml"):
        if os.path.exists(f"{R}/drawable/{f}"):
            os.remove(f"{R}/drawable/{f}")
    render(1556, "fg", 1.45).crop((0, 0, 1556, 1556)).save(R + "/drawable/img_launcher.png")
    open(R + "/values/ic_launcher_background.xml", "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0B1020</color>\n</resources>\n')
print("CxdElite branding applied.")
