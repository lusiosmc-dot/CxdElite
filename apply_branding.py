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
PHASE_LITE           = True   # Lite: no live blur (baked into wallpaper), much smoother on weak phones
PHASE_RELEASE_BUILD  = True   # Release (optimized) build instead of slow debug build; signed with the repo's debug key
PHASE_NEW_HOME       = True   # NEW landscape home: two left bars + centered launch card (needs PORTRAIT + ROTATE phases)
PHASE_INTRO          = True   # 3-second animated loading screen when the launcher opens
PHASE_GLASS_ALL      = True   # glass top bar on every page + glass popups/dialogs
PHASE_PORTRAIT_FIXES = True   # Portrait: 2-row top bar (title row + buttons row), no skin on Account page
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
    (r"(?m)^launcher_version_name=.*", "launcher_version_name=4.7.2"),
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
        ('intSetting("backgroundBlur", 0, 0..40)', 'intSetting("backgroundBlur", %d, 0..40)' % (0 if PHASE_LITE else 24), 1),
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
    from PIL import ImageFilter as _F
    _w = _I.open("logo.png").convert("RGB")
    if PHASE_LITE:   # frosted-glass look baked into the picture = zero blur cost while running
        _w = _w.resize((960, 960)).filter(_F.GaussianBlur(8))
    else:
        _w = _w.resize((1080, 1080))
    _w.save(M + "/assets/cxdelite_bg.jpg", "JPEG", quality=88)
    patch(K + "/ZLApplication.kt", [
        ("            DEVICE_ARCHITECTURE = Architecture.getDeviceArchitecture()\n",
         "            DEVICE_ARCHITECTURE = Architecture.getDeviceArchitecture()\n"
         "            //CxdElite: first-run default glass wallpaper\n"
         "            runCatching {\n"
         "                val bg = PathManager.FILE_LAUNCHER_BACKGROUND\n"
         "                val mark = java.io.File(bg.parentFile, \".cxd_seeded2\")\n"
         "                if (!mark.exists()) {\n"
         "                    bg.parentFile?.mkdirs()\n"
         "                    assets.open(\"cxdelite_bg.jpg\").use { i -> bg.outputStream().use { o -> i.copyTo(o) } }\n"
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
                    onClick = {
                        runCatching {
                            cxdCtx.startActivity(
                                android.content.Intent(
                                    android.content.Intent.ACTION_VIEW,
                                    android.net.Uri.parse("https://www.youtube.com/@hexablockyt-b1t")
                                ).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
                            )
                        }
                    }
                ) {
                    Icon(
                        painter = painterResource(R.drawable.ic_cxd_youtube),
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

if PHASE_RELEASE_BUILD:
    patch("ZalithLauncher/build.gradle.kts", [
        ('signingConfig = signingConfigs.getByName("releaseBuild")', 'signingConfig = signingConfigs.getByName("debugBuild")', 1),
    ])

if PHASE_ROTATE_BUTTON:
    open(R + "/drawable/ic_cxd_youtube.xml", "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">\n'
        '    <path android:fillColor="#FF000000" android:fillType="evenOdd"\n'
        '        android:pathData="M21.6,7.2c-0.2,-0.9 -0.9,-1.5 -1.8,-1.7C18.3,5.2 12,5.2 12,5.2s-6.3,0 -7.8,0.3C3.3,5.7 2.6,6.3 2.4,7.2 2,8.7 2,12 2,12s0,3.3 0.4,4.8c0.2,0.9 0.9,1.5 1.8,1.7 1.5,0.3 7.8,0.3 7.8,0.3s6.3,0 7.8,-0.3c0.9,-0.2 1.6,-0.8 1.8,-1.7C22,15.3 22,12 22,12s0,-3.3 -0.4,-4.8zM10,15L10,9l5.2,3z"/>\n'
        '</vector>\n')

if PHASE_LITE:
    _t = open(K + "/setting/AllSettings.kt", encoding="utf-8").read()
    assert "TransitionAnimationType.JELLY_BOUNCE)" in _t
    _t = _t.replace("TransitionAnimationType.JELLY_BOUNCE)", "TransitionAnimationType.SLICE_IN)")
    open(K + "/setting/AllSettings.kt", "w", encoding="utf-8").write(_t)

if PHASE_NEW_HOME and PHASE_PORTRAIT and PHASE_ROTATE_BUTTON:
    # ---- LauncherScreen: new landscape layout (card centered in the space right of the bars) ----
    NEW_LAND = """            } else if (true) {
                if (maxWidth < maxHeight) {
                    CxdPortraitHome(
                        onLaunchGame = onLaunchGame,
                        toAccountManageScreen = toAccountManageScreen,
                        toVersionManageScreen = toVersionManageScreen,
                        toVersionSettingsScreen = toVersionSettingsScreen
                    )
                } else {
                    CxdLandscapeHome(
                        onLaunchGame = onLaunchGame,
                        toAccountManageScreen = toAccountManageScreen,
                        toVersionManageScreen = toVersionManageScreen,
                        toVersionSettingsScreen = toVersionSettingsScreen
                    )
                }
            } else {
"""
    patch(K + "/ui/screens/content/LauncherScreen.kt", [
        ("import androidx.compose.foundation.layout.Row\n",
         "import androidx.compose.foundation.layout.Row\nimport androidx.compose.foundation.layout.fillMaxHeight\n"
         "import androidx.compose.foundation.gestures.awaitEachGesture\nimport androidx.compose.foundation.gestures.awaitFirstDown\n"
         "import androidx.compose.foundation.gestures.waitForUpOrCancellation\nimport androidx.compose.ui.input.pointer.pointerInput\n", 1),
        ("            } else {\n            // 内容区域\n", NEW_LAND + "            // 内容区域\n", 1),
        ("            if (maxWidth < maxHeight) {\n                CompositionLocalProvider(\n",
         "            if (false) {\n                CompositionLocalProvider(\n", 1),
    ])
    with open(K + "/ui/screens/content/LauncherScreen.kt", "a", encoding="utf-8") as _f:
        _f.write("\n\n/** CxdElite: total width reserved on the left for the two bars of the landscape home */\ninternal val CXD_BARS_WIDTH: androidx.compose.ui.unit.Dp = 150.dp\n")

    # ---- MainScreen: hide the top bar on the landscape home, draw the two left bars instead ----
    BARS_CALL = """                    submitError = submitError
                )

                if (inLauncherScreen) {
                    val cxdToAccounts: () -> Unit = {
                        screenBackStackModel.mainScreen.navigateTo(
                            screenKey = NormalNavKey.AccountManager(com.movtery.zalithlauncher.ui.screens.content.FirstLoginMenu.NONE)
                        )
                    }
                    val cxdToVersions: () -> Unit = {
                        screenBackStackModel.mainScreen.removeAndNavigateTo(
                            remove = NestedNavKey.VersionSettings::class,
                            screenKey = NormalNavKey.VersionsManager
                        )
                    }
                    val cxdToDownload: () -> Unit = { screenBackStackModel.navigateToDownload() }
                    val cxdToSettings: () -> Unit = {
                        screenBackStackModel.mainScreen.removeAndNavigateTo(
                            removes = screenBackStackModel.clearBeforeNavKeys,
                            screenKey = screenBackStackModel.settingsScreen
                        )
                    }
                    val cxdToMultiplayer: () -> Unit = {
                        screenBackStackModel.mainScreen.removeAndNavigateTo(
                            removes = screenBackStackModel.clearBeforeNavKeys,
                            screenKey = NormalNavKey.Multiplayer
                        )
                    }
                    val cxdOpenFiles: () -> Unit = {
                        eventViewModel.sendEvent(
                            EventViewModel.Event.OpenFileManager(
                                rootPath = PathManager.DIR_FILES_EXTERNAL.absolutePath
                            )
                        )
                    }
                    if (cxdLandscapeHome) {
                        CxdHomeBars(
                            modifier = Modifier.align(Alignment.CenterStart),
                            toAccounts = cxdToAccounts,
                            toVersions = cxdToVersions,
                            toDownload = cxdToDownload,
                            toSettings = cxdToSettings,
                            toMultiplayer = cxdToMultiplayer,
                            openFiles = cxdOpenFiles
                        )
                    } else {
                        CxdHomeBarsPortrait(
                            modifier = Modifier.align(Alignment.BottomCenter),
                            toAccounts = cxdToAccounts,
                            toVersions = cxdToVersions,
                            toDownload = cxdToDownload,
                            toSettings = cxdToSettings,
                            toMultiplayer = cxdToMultiplayer,
                            openFiles = cxdOpenFiles
                        )
                    }
                }

                TaskMenu("""
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("    val inLauncherScreen = mainScreenKey == null || mainScreenKey is NormalNavKey.LauncherMain\n",
         "    val inLauncherScreen = mainScreenKey == null || mainScreenKey is NormalNavKey.LauncherMain\n"
         "    val cxdLandscapeHome = inLauncherScreen &&\n"
         "        androidx.compose.ui.platform.LocalConfiguration.current.orientation == android.content.res.Configuration.ORIENTATION_LANDSCAPE\n", 1),
        ("            TopBar(\n                modifier = Modifier\n                    .fillMaxWidth()\n                    .height(40.dp),",
         "            if (!inLauncherScreen) TopBar(\n                modifier = Modifier\n                    .fillMaxWidth()\n                    .height(40.dp),", 1),
        ("                    submitError = submitError\n                )\n\n                TaskMenu(", BARS_CALL, 1),
    ])
    with open(K + "/ui/screens/main/MainScreen.kt", "a", encoding="utf-8") as _f:
        _f.write("""

/** CxdElite: landscape home = two glass bars on the left (4 main buttons + 4 tools) with the launcher name under them */
@Composable
private fun CxdHomeBars(
    modifier: Modifier = Modifier,
    toAccounts: () -> Unit,
    toVersions: () -> Unit,
    toDownload: () -> Unit,
    toSettings: () -> Unit,
    toMultiplayer: () -> Unit,
    openFiles: () -> Unit,
) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val rotate: () -> Unit = {
        var c: android.content.Context = ctx
        while (c is android.content.ContextWrapper && c !is android.app.Activity) c = c.baseContext
        (c as? android.app.Activity)?.let { a ->
            val toPortrait = a.resources.configuration.orientation != android.content.res.Configuration.ORIENTATION_PORTRAIT
            a.requestedOrientation = if (toPortrait) android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                else android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
            a.getSharedPreferences("cxd", 0).edit().putBoolean("portrait", toPortrait).apply()
        }
    }
    val youtube: () -> Unit = {
        runCatching {
            ctx.startActivity(
                android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse("https://www.youtube.com/@hexablockyt-b1t")
                ).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
            )
        }
    }
    Column(
        modifier = modifier
            .fillMaxHeight()
            .width(com.movtery.zalithlauncher.ui.screens.content.CXD_BARS_WIDTH)
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Row(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            BackgroundCard(modifier = Modifier.weight(1f).fillMaxHeight().cxdMovable("bar1")) {
                Column(modifier = Modifier.fillMaxSize().padding(vertical = 4.dp)) {
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_person_outlined), "Accounts", toAccounts)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_list_alt_check_outlined), "Versions", toVersions)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_download_2_filled), "Download", toDownload)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_settings_filled), "Settings", toSettings)
                }
            }
            BackgroundCard(modifier = Modifier.weight(1f).fillMaxHeight().cxdMovable("bar2")) {
                Column(modifier = Modifier.fillMaxSize().padding(vertical = 4.dp)) {
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_mobile_rotate_filled), "Rotate", rotate)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_cxd_youtube), "YouTube", youtube)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_folder_filled), "Files", openFiles)
                    CxdBarItem(Modifier.weight(1f).fillMaxWidth(), painterResource(R.drawable.ic_group_filled), "Together", toMultiplayer)
                }
            }
        }
        Text(
            modifier = Modifier.fillMaxWidth(),
            text = BuildKeys.LAUNCHER_NAME,
            maxLines = 2,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            fontSize = androidx.compose.ui.unit.TextUnit(11f, androidx.compose.ui.unit.TextUnitType.Sp)
        )
    }
}

@Composable
private fun CxdBarItem(
    modifier: Modifier = Modifier,
    painter: androidx.compose.ui.graphics.painter.Painter,
    text: String,
    onClick: () -> Unit
) {
    Column(
        modifier = modifier
            .clip(MaterialTheme.shapes.large)
            .clickable(onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            painter = painter,
            contentDescription = text,
            modifier = Modifier.size(22.dp)
        )
        Text(
            text = text,
            maxLines = 1,
            fontSize = androidx.compose.ui.unit.TextUnit(10f, androidx.compose.ui.unit.TextUnitType.Sp)
        )
    }
}
""")

if PHASE_NEW_HOME and PHASE_PORTRAIT and PHASE_ROTATE_BUTTON:
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("import com.movtery.zalithlauncher.ui.screens.NestedNavKey\n",
         "import com.movtery.zalithlauncher.ui.screens.NestedNavKey\nimport com.movtery.zalithlauncher.ui.screens.content.cxdMovable\n", 1),
    ])
    # skin keeps rotating in a loop
    patch(M + "/assets/skinview/skinview.js", [
        ("\nsetAzimuthAndPitch(0, 10);\n",
         "\nsetAzimuthAndPitch(0, 10);\nskinViewer.autoRotate = true;\nskinViewer.autoRotateSpeed = 0.7;\n", 1),
    ])
    with open(K + "/ui/screens/content/CxdHomeEdit.kt", "w", encoding="utf-8") as _f:
        _f.write("""package com.movtery.zalithlauncher.ui.screens.content

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChange
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import kotlin.math.abs
import kotlin.math.roundToInt

/** CxdElite: edit mode + saved positions for the home items. Items never overlap, stay inside the screen and snap on release. */
object CxdHomeEdit {
    var editing by mutableStateOf(false)
    var density: Float = 2f
    private val offsets = mutableStateMapOf<String, Offset>()
    private val bounds = HashMap<String, Rect>()
    private var prefs: SharedPreferences? = null

    fun init(context: Context) {
        if (prefs != null) return
        val p = context.applicationContext.getSharedPreferences("cxd_home", Context.MODE_PRIVATE)
        prefs = p
        for ((k, v) in p.all) {
            if (k.endsWith("_x") && v is Float) {
                val key = k.removeSuffix("_x")
                offsets[key] = Offset(v, p.getFloat(key + "_y", 0f))
            }
        }
    }

    fun offsetOf(key: String): Offset = offsets[key] ?: Offset.Zero

    fun setBounds(key: String, r: Rect) {
        bounds[key] = r
    }

    fun clearBounds(key: String) {
        bounds.remove(key)
    }

    private fun overlapsOthers(key: String, r: Rect): Boolean {
        for ((k, o) in bounds) {
            if (k == key) continue
            if (r.left < o.right && r.right > o.left && r.top < o.bottom && r.bottom > o.top) return true
        }
        return false
    }

    private fun inside(r: Rect, w: Float, h: Float): Boolean =
        r.left >= 0f && r.top >= 0f && r.right <= w && r.bottom <= h

    private fun ok(key: String, r: Rect, w: Float, h: Float): Boolean =
        inside(r, w, h) && !overlapsOthers(key, r)

    private fun apply(key: String, d: Offset, r: Rect) {
        offsets[key] = offsetOf(key) + d
        bounds[key] = r.translate(d)
    }

    /** drag step: keep inside the screen, never overlap another item (slides along the other item if possible) */
    fun move(key: String, delta: Offset, w: Float, h: Float) {
        val r = bounds[key]
        if (r == null) {
            offsets[key] = offsetOf(key) + delta
            return
        }
        var d = delta
        val nr = r.translate(d)
        if (nr.left < 0f) d = Offset(d.x - nr.left, d.y)
        if (nr.right > w) d = Offset(d.x - (nr.right - w), d.y)
        if (nr.top < 0f) d = Offset(d.x, d.y - nr.top)
        if (nr.bottom > h) d = Offset(d.x, d.y - (nr.bottom - h))
        val tries = listOf(d, Offset(d.x, 0f), Offset(0f, d.y))
        for (t in tries) {
            if (t == Offset.Zero) continue
            if (!overlapsOthers(key, r.translate(t))) {
                apply(key, t, r)
                return
            }
        }
    }

    /** on release: snap to screen edges / neighbours when close, then save */
    fun snap(key: String, w: Float, h: Float) {
        val r = bounds[key]
        if (r != null) {
            val th = 28f * density
            val margin = 8f * density
            val gap = 10f * density
            val xs = arrayListOf(margin, w - margin - r.width)
            val ys = arrayListOf(margin, h - margin - r.height)
            for ((k, o) in bounds) {
                if (k == key) continue
                xs.addAll(listOf(o.left, o.right - r.width, o.right + gap, o.left - gap - r.width))
                ys.addAll(listOf(o.top, o.bottom - r.height, o.bottom + gap, o.top - gap - r.height))
            }
            val dx = xs.map { it - r.left }.filter { abs(it) <= th }.minByOrNull { abs(it) } ?: 0f
            val dy = ys.map { it - r.top }.filter { abs(it) <= th }.minByOrNull { abs(it) } ?: 0f
            val both = Offset(dx, dy)
            if (both != Offset.Zero && ok(key, r.translate(both), w, h)) {
                apply(key, both, r)
            } else if (dx != 0f && ok(key, r.translate(Offset(dx, 0f)), w, h)) {
                apply(key, Offset(dx, 0f), r)
            } else if (dy != 0f && ok(key, r.translate(Offset(0f, dy)), w, h)) {
                apply(key, Offset(0f, dy), r)
            }
        }
        save(key)
    }

    fun save(key: String) {
        val o = offsetOf(key)
        prefs?.edit()?.putFloat(key + "_x", o.x)?.putFloat(key + "_y", o.y)?.apply()
    }

    fun reset() {
        offsets.clear()
        prefs?.edit()?.clear()?.apply()
    }
}

/** Moves the item by its saved offset; in edit mode the item can be dragged (touches never reach the buttons inside) */
@Composable
fun Modifier.cxdMovable(key: String): Modifier {
    val ctx = LocalContext.current
    val view = LocalView.current
    val density = LocalDensity.current.density
    remember(ctx) { CxdHomeEdit.init(ctx) }
    CxdHomeEdit.density = density
    DisposableEffect(key) {
        onDispose { CxdHomeEdit.clearBounds(key) }
    }
    val editing = CxdHomeEdit.editing
    val base = this
        .offset {
            val o = CxdHomeEdit.offsetOf(key)
            IntOffset(o.x.roundToInt(), o.y.roundToInt())
        }
        .onGloballyPositioned { CxdHomeEdit.setBounds(key, it.boundsInRoot()) }
    if (!editing) return base
    return base
        .border(2.dp, Color.White.copy(alpha = 0.7f), RoundedCornerShape(24.dp))
        .pointerInput(key) {
            awaitEachGesture {
                val down = awaitFirstDown(requireUnconsumed = false, pass = PointerEventPass.Initial)
                down.consume()
                val id = down.id
                while (true) {
                    val event = awaitPointerEvent(PointerEventPass.Initial)
                    val change = event.changes.firstOrNull { it.id == id } ?: break
                    if (!change.pressed) {
                        CxdHomeEdit.snap(key, view.width.toFloat(), view.height.toFloat())
                        break
                    }
                    val d = change.positionChange()
                    if (d != Offset.Zero) CxdHomeEdit.move(key, d, view.width.toFloat(), view.height.toFloat())
                    change.consume()
                }
            }
        }
}
""")
    with open(K + "/ui/screens/content/LauncherScreen.kt", "a", encoding="utf-8") as _f:
        _f.write("""

/** CxdElite: landscape home. Skin box + account card + version card stick to the right edge.
 *  Hold an empty spot for 2 seconds -> edit mode (drag any item, positions are saved). */
@Composable
private fun CxdLandscapeHome(
    onLaunchGame: (Version?) -> Unit,
    toAccountManageScreen: () -> Unit,
    toVersionManageScreen: () -> Unit,
    toVersionSettingsScreen: () -> Unit,
) {
    val account by AccountsManager.currentAccountFlow.collectAsStateWithLifecycle()
    val refreshWardrobe by AccountsManager.refreshWardrobe.collectAsStateWithLifecycle()
    val skinFile = remember(account, refreshWardrobe) {
        account?.getSkinFile()?.takeIf { it.exists() }
    }
    val capeFile = remember(account, refreshWardrobe) {
        account?.getCapeFile()?.takeIf { it.exists() }
    }
    val editing = CxdHomeEdit.editing

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                awaitEachGesture {
                    awaitFirstDown()
                    val t0 = System.currentTimeMillis()
                    val up = withTimeoutOrNull(2000L) { waitForUpOrCancellation() }
                    if (up == null && System.currentTimeMillis() - t0 >= 1900L && !CxdHomeEdit.editing) {
                        CxdHomeEdit.editing = true
                    }
                }
            }
    ) {
        Column(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .fillMaxHeight()
                .width(340.dp)
                .padding(8.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            BackgroundCard(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .cxdMovable("skin"),
                shape = MaterialTheme.shapes.extraLarge
            ) {
                SkinPreview3D(
                    modifier = Modifier.fillMaxSize(),
                    skinFile = skinFile,
                    capeFile = capeFile,
                    modelType = account?.skinModelType,
                    interactionEnabled = false,
                    azimuth = -35,
                    refreshKey = listOf(account?.uniqueUUID, refreshWardrobe, skinFile?.lastModified() ?: 0L, capeFile?.lastModified() ?: 0L)
                )
            }

            BackgroundCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .cxdMovable("account"),
                shape = MaterialTheme.shapes.extraLarge,
                onClick = { if (!editing) toAccountManageScreen() }
            ) {
                AccountAvatarRow(
                    modifier = Modifier.fillMaxWidth(),
                    account = account,
                )
            }

            BackgroundCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .cxdMovable("version"),
                shape = MaterialTheme.shapes.extraLarge,
            ) {
                VersionsContent(
                    modifier = Modifier.fillMaxWidth(),
                    onLaunchGame = onLaunchGame,
                    toVersionManageScreen = toVersionManageScreen,
                    toVersionSettingsScreen = toVersionSettingsScreen,
                )
            }
        }

        if (editing) {
            Row(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                androidx.compose.material3.Button(onClick = { CxdHomeEdit.reset() }) {
                    Text(text = "Reset")
                }
                androidx.compose.material3.Button(onClick = { CxdHomeEdit.editing = false }) {
                    Text(text = "Done")
                }
            }
        }
    }
}
""")

if PHASE_NEW_HOME and PHASE_PORTRAIT and PHASE_ROTATE_BUTTON:
    with open(K + "/ui/screens/main/MainScreen.kt", "a", encoding="utf-8") as _f:
        _f.write("""

/** CxdElite: portrait home = two glass bars at the bottom (4 main buttons + 4 tools) with the launcher name under them */
@Composable
private fun CxdHomeBarsPortrait(
    modifier: Modifier = Modifier,
    toAccounts: () -> Unit,
    toVersions: () -> Unit,
    toDownload: () -> Unit,
    toSettings: () -> Unit,
    toMultiplayer: () -> Unit,
    openFiles: () -> Unit,
) {
    val ctx = androidx.compose.ui.platform.LocalContext.current
    val rotate: () -> Unit = {
        var c: android.content.Context = ctx
        while (c is android.content.ContextWrapper && c !is android.app.Activity) c = c.baseContext
        (c as? android.app.Activity)?.let { a ->
            val toPortrait = a.resources.configuration.orientation != android.content.res.Configuration.ORIENTATION_PORTRAIT
            a.requestedOrientation = if (toPortrait) android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                else android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
            a.getSharedPreferences("cxd", 0).edit().putBoolean("portrait", toPortrait).apply()
        }
    }
    val youtube: () -> Unit = {
        runCatching {
            ctx.startActivity(
                android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse("https://www.youtube.com/@hexablockyt-b1t")
                ).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
            )
        }
    }
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        BackgroundCard(
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp)
                .cxdMovable("p_bar1")
        ) {
            Row(modifier = Modifier.fillMaxSize().padding(horizontal = 4.dp)) {
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_person_outlined), "Accounts", toAccounts)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_list_alt_check_outlined), "Versions", toVersions)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_download_2_filled), "Download", toDownload)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_settings_filled), "Settings", toSettings)
            }
        }
        BackgroundCard(
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp)
                .cxdMovable("p_bar2")
        ) {
            Row(modifier = Modifier.fillMaxSize().padding(horizontal = 4.dp)) {
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_mobile_rotate_filled), "Rotate", rotate)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_cxd_youtube), "YouTube", youtube)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_folder_filled), "Files", openFiles)
                CxdBarItem(Modifier.weight(1f).fillMaxHeight(), painterResource(R.drawable.ic_group_filled), "Together", toMultiplayer)
            }
        }
        Text(
            modifier = Modifier.fillMaxWidth(),
            text = BuildKeys.LAUNCHER_NAME,
            maxLines = 1,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            fontSize = androidx.compose.ui.unit.TextUnit(11f, androidx.compose.ui.unit.TextUnitType.Sp)
        )
    }
}
""")
    with open(K + "/ui/screens/content/LauncherScreen.kt", "a", encoding="utf-8") as _f:
        _f.write("""

/** space kept free at the bottom of the portrait home for the two bars + name label */
internal val CXD_PORTRAIT_BARS_HEIGHT: androidx.compose.ui.unit.Dp = 192.dp

/** CxdElite: portrait home. Skin box on top, then account card, then version card; the two bars sit at the bottom. */
@Composable
private fun CxdPortraitHome(
    onLaunchGame: (Version?) -> Unit,
    toAccountManageScreen: () -> Unit,
    toVersionManageScreen: () -> Unit,
    toVersionSettingsScreen: () -> Unit,
) {
    val account by AccountsManager.currentAccountFlow.collectAsStateWithLifecycle()
    val refreshWardrobe by AccountsManager.refreshWardrobe.collectAsStateWithLifecycle()
    val skinFile = remember(account, refreshWardrobe) {
        account?.getSkinFile()?.takeIf { it.exists() }
    }
    val capeFile = remember(account, refreshWardrobe) {
        account?.getCapeFile()?.takeIf { it.exists() }
    }
    val editing = CxdHomeEdit.editing

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                awaitEachGesture {
                    awaitFirstDown()
                    val t0 = System.currentTimeMillis()
                    val up = withTimeoutOrNull(2000L) { waitForUpOrCancellation() }
                    if (up == null && System.currentTimeMillis() - t0 >= 1900L && !CxdHomeEdit.editing) {
                        CxdHomeEdit.editing = true
                    }
                }
            }
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(start = 8.dp, end = 8.dp, top = 8.dp, bottom = CXD_PORTRAIT_BARS_HEIGHT),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            BackgroundCard(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .cxdMovable("p_skin"),
                shape = MaterialTheme.shapes.extraLarge
            ) {
                SkinPreview3D(
                    modifier = Modifier.fillMaxSize(),
                    skinFile = skinFile,
                    capeFile = capeFile,
                    modelType = account?.skinModelType,
                    interactionEnabled = false,
                    azimuth = -35,
                    refreshKey = listOf(account?.uniqueUUID, refreshWardrobe, skinFile?.lastModified() ?: 0L, capeFile?.lastModified() ?: 0L)
                )
            }

            BackgroundCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .cxdMovable("p_account"),
                shape = MaterialTheme.shapes.extraLarge,
                onClick = { if (!editing) toAccountManageScreen() }
            ) {
                AccountAvatarRow(
                    modifier = Modifier.fillMaxWidth(),
                    account = account,
                )
            }

            BackgroundCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .cxdMovable("p_version"),
                shape = MaterialTheme.shapes.extraLarge,
            ) {
                VersionsContent(
                    modifier = Modifier.fillMaxWidth(),
                    onLaunchGame = onLaunchGame,
                    toVersionManageScreen = toVersionManageScreen,
                    toVersionSettingsScreen = toVersionSettingsScreen,
                )
            }
        }

        if (editing) {
            Row(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                androidx.compose.material3.Button(onClick = { CxdHomeEdit.reset() }) {
                    Text(text = "Reset")
                }
                androidx.compose.material3.Button(onClick = { CxdHomeEdit.editing = false }) {
                    Text(text = "Done")
                }
            }
        }
    }
}
""")

if PHASE_GLASS_ALL:
    # popups / dialogs: glass container + thin border
    _d = open(K + "/ui/components/Dialogs.kt", encoding="utf-8").read()
    assert _d.count("color = cardColor(false),") == 4 and _d.count("\n    AlertDialog(\n") == 3
    _d = _d.replace("color = cardColor(false),",
                    "color = cardColor(false).copy(alpha = 0.88f),\n                border = BorderStroke(1.dp, Color.White.copy(alpha = 0.18f)),")
    _d = _d.replace("\n    AlertDialog(\n", "\n    AlertDialog(\n        containerColor = cardColor(false).copy(alpha = 0.88f),\n")
    _d = _d.replace("import androidx.compose.ui.window.DialogProperties\n",
                    "import androidx.compose.ui.window.DialogProperties\nimport androidx.compose.foundation.BorderStroke\nimport androidx.compose.ui.graphics.Color\n", 1)
    open(K + "/ui/components/Dialogs.kt", "w", encoding="utf-8").write(_d)
    # top bar of every page = glass pill
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("                modifier = Modifier\n                    .fillMaxWidth()\n                    .height(40.dp),",
         "                modifier = Modifier\n                    .fillMaxWidth()\n"
         "                    .padding(horizontal = 8.dp, vertical = 4.dp)\n"
         "                    .height(if (androidx.compose.ui.platform.LocalConfiguration.current.orientation == android.content.res.Configuration.ORIENTATION_PORTRAIT) 96.dp else 44.dp)\n"
         "                    .clip(RoundedCornerShape(22.dp))\n"
         "                    .background(Color.White.copy(alpha = 0.07f))\n"
         "                    .border(1.dp, Color.White.copy(alpha = 0.18f), RoundedCornerShape(22.dp))\n"
         "                    .padding(horizontal = 6.dp),", 1),
        ("import androidx.compose.ui.unit.dp\n",
         "import androidx.compose.ui.unit.dp\nimport androidx.compose.foundation.background\nimport androidx.compose.foundation.border\n"
         "import androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.ui.graphics.Color\n", 1),
    ])

if PHASE_INTRO:
    with open(K + "/ui/screens/content/CxdIntro.kt", "w", encoding="utf-8") as _f:
        _f.write("""package com.movtery.zalithlauncher.ui.screens.content

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.movtery.zalithlauncher.BuildKeys
import com.movtery.zalithlauncher.R
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/** CxdElite: the intro plays only once per app process */
object CxdIntroState {
    var shown: Boolean = false
}

/** CxdElite: ~3 second loading animation (logo pops in, ring spins, progress bar fills, then fades out) */
@Composable
fun CxdIntro(onFinished: () -> Unit) {
    val logoScale = remember { Animatable(0.6f) }
    val logoAlpha = remember { Animatable(0f) }
    val textAlpha = remember { Animatable(0f) }
    val progress = remember { Animatable(0f) }
    val exit = remember { Animatable(1f) }
    val infinite = rememberInfiniteTransition(label = "cxdIntro")
    val ringAngle by infinite.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(1800, easing = LinearEasing)),
        label = "ring"
    )

    LaunchedEffect(Unit) {
        launch { logoAlpha.animateTo(1f, tween(500)) }
        launch { logoScale.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = 140f)) }
        launch {
            delay(700)
            textAlpha.animateTo(1f, tween(600))
        }
        launch { progress.animateTo(1f, tween(2600, easing = FastOutSlowInEasing)) }
        delay(2600)
        exit.animateTo(0f, tween(400))
        onFinished()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .graphicsLayer { alpha = exit.value }
            .background(
                Brush.verticalGradient(
                    listOf(Color(0xFF04060B), Color(0xFF121826), Color(0xFF04060B))
                )
            )
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = {}
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Box(
                modifier = Modifier.size(200.dp),
                contentAlignment = Alignment.Center
            ) {
                Canvas(
                    modifier = Modifier
                        .fillMaxSize()
                        .graphicsLayer { alpha = logoAlpha.value }
                ) {
                    rotate(ringAngle) {
                        drawCircle(
                            brush = Brush.sweepGradient(
                                listOf(Color.Transparent, Color(0xFF00E5FF), Color(0xFF7C4DFF), Color.Transparent)
                            ),
                            radius = size.minDimension / 2f - 4.dp.toPx(),
                            style = Stroke(width = 5.dp.toPx(), cap = StrokeCap.Round)
                        )
                    }
                }
                Image(
                    painter = painterResource(R.drawable.img_launcher),
                    contentDescription = null,
                    modifier = Modifier
                        .size(132.dp)
                        .graphicsLayer {
                            scaleX = logoScale.value
                            scaleY = logoScale.value
                            alpha = logoAlpha.value
                        }
                        .clip(RoundedCornerShape(28.dp))
                )
            }
            Spacer(modifier = Modifier.height(20.dp))
            Text(
                text = BuildKeys.LAUNCHER_NAME,
                color = Color.White,
                fontSize = 22.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.graphicsLayer { alpha = textAlpha.value }
            )
            Spacer(modifier = Modifier.height(18.dp))
            Box(
                modifier = Modifier
                    .width(180.dp)
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(Color.White.copy(alpha = 0.15f))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(progress.value)
                        .background(Brush.horizontalGradient(listOf(Color(0xFF00E5FF), Color(0xFF7C4DFF))))
                )
            }
        }
    }
}
""")
    patch(K + "/ui/activities/MainActivity.kt", [
        ("        //处理外部导入",
         "        //CxdElite: 3 second loading screen, shown once per app start (overlay above everything)\n"
         "        if (!com.movtery.zalithlauncher.ui.screens.content.CxdIntroState.shown) {\n"
         "            com.movtery.zalithlauncher.ui.screens.content.CxdIntroState.shown = true\n"
         "            window.decorView.post {\n"
         "                val introView = androidx.compose.ui.platform.ComposeView(this)\n"
         "                introView.setContent {\n"
         "                    com.movtery.zalithlauncher.ui.screens.content.CxdIntro(\n"
         "                        onFinished = { (introView.parent as? android.view.ViewGroup)?.removeView(introView) }\n"
         "                    )\n"
         "                }\n"
         "                addContentView(\n"
         "                    introView,\n"
         "                    android.view.ViewGroup.LayoutParams(\n"
         "                        android.view.ViewGroup.LayoutParams.MATCH_PARENT,\n"
         "                        android.view.ViewGroup.LayoutParams.MATCH_PARENT\n"
         "                    )\n"
         "                )\n"
         "            }\n"
         "        }\n"
         "        //处理外部导入", 1),
    ])

if PHASE_PORTRAIT_FIXES and PHASE_GLASS_ALL:
    # ---- two-row top bar in portrait: row 1 = back, home, title / row 2 = all the buttons spread evenly ----
    patch(K + "/ui/screens/main/MainScreen.kt", [
        ("            val (backCenter, title, endButtons) = createRefs()\n",
         "            val (backCenter, title, endButtons) = createRefs()\n"
         "            val cxdTwoRows = androidx.compose.ui.platform.LocalConfiguration.current.orientation ==\n"
         "                android.content.res.Configuration.ORIENTATION_PORTRAIT\n"
         "            val cxdMid = createGuidelineFromTop(0.5f)\n", 1),
        ("                    .constrainAs(backCenter) {\n                        start.linkTo(parent.start)\n                        top.linkTo(parent.top)\n                        bottom.linkTo(parent.bottom)\n                    }\n",
         "                    .constrainAs(backCenter) {\n                        start.linkTo(parent.start)\n                        top.linkTo(parent.top)\n"
         "                        bottom.linkTo(if (cxdTwoRows) cxdMid else parent.bottom)\n"
         "                        if (cxdTwoRows) height = androidx.constraintlayout.compose.Dimension.fillToConstraints\n"
         "                    }\n", 1),
        ("                modifier = Modifier.constrainAs(title) {\n                    centerVerticallyTo(parent)\n                    start.linkTo(backCenter.end, margin = 16.dp)\n                },\n",
         "                modifier = Modifier.constrainAs(title) {\n"
         "                    if (cxdTwoRows) {\n                        top.linkTo(parent.top)\n                        bottom.linkTo(cxdMid)\n                    } else {\n                        centerVerticallyTo(parent)\n                    }\n"
         "                    start.linkTo(backCenter.end, margin = 16.dp)\n                },\n", 1),
        ("                    .constrainAs(endButtons) {\n                        top.linkTo(parent.top)\n                        bottom.linkTo(parent.bottom)\n                        end.linkTo(parent.end, margin = 12.dp)\n                    },\n                verticalAlignment = Alignment.CenterVertically,\n                horizontalArrangement = Arrangement.spacedBy(8.dp)\n",
         "                    .constrainAs(endButtons) {\n"
         "                        if (cxdTwoRows) {\n"
         "                            top.linkTo(cxdMid)\n"
         "                            bottom.linkTo(parent.bottom)\n"
         "                            start.linkTo(parent.start, margin = 4.dp)\n"
         "                            end.linkTo(parent.end, margin = 4.dp)\n"
         "                            width = androidx.constraintlayout.compose.Dimension.fillToConstraints\n"
         "                            height = androidx.constraintlayout.compose.Dimension.fillToConstraints\n"
         "                        } else {\n"
         "                            top.linkTo(parent.top)\n"
         "                            bottom.linkTo(parent.bottom)\n"
         "                            end.linkTo(parent.end, margin = 12.dp)\n"
         "                        }\n"
         "                    },\n"
         "                verticalAlignment = Alignment.CenterVertically,\n"
         "                horizontalArrangement = if (cxdTwoRows) Arrangement.SpaceEvenly else Arrangement.spacedBy(8.dp)\n", 1),
    ])

if PHASE_PORTRAIT_FIXES:
    # ---- Account page: no skin preview in portrait, "Add account" button on top, list below ----
    patch(K + "/ui/screens/content/AccountManageScreen.kt", [
        ("    Row(\n        modifier = Modifier.fillMaxSize()\n    ) {\n        ActionsLayout(\n",
         "    val cxdPortraitAcc = androidx.compose.ui.platform.LocalConfiguration.current.orientation ==\n"
         "        android.content.res.Configuration.ORIENTATION_PORTRAIT\n"
         "    Row(\n        modifier = Modifier.fillMaxSize()\n    ) {\n"
         "        if (cxdPortraitAcc) {\n"
         "            Column(modifier = Modifier.fillMaxSize()) {\n"
         "                ScalingActionButton(\n"
         "                    modifier = Modifier\n"
         "                        .fillMaxWidth()\n"
         "                        .padding(start = 12.dp, end = 12.dp, top = 12.dp),\n"
         "                    onClick = {\n"
         "                        actions.onIntent(AccountManageIntent.UpdateLoginMenuOp(LoginMenuOperation.Login))\n"
         "                    }\n"
         "                ) {\n"
         "                    MarqueeText(text = stringResource(R.string.account_add_new_account))\n"
         "                }\n"
         "                AccountsLayout(\n"
         "                    isVisible = isVisible,\n"
         "                    modifier = Modifier\n"
         "                        .weight(1f)\n"
         "                        .fillMaxWidth()\n"
         "                        .padding(all = 12.dp),\n"
         "                    accounts = profileUiState.accounts,\n"
         "                    currentAccount = profileUiState.currentAccount,\n"
         "                    accountOperation = operationUiState.accountOp,\n"
         "                    accountSkinOperation = operationUiState.accountSkinOp,\n"
         "                    accountSkinDialogState = operationUiState.accountSkinDialogState,\n"
         "                    accountCapes = profileUiState.accountCapeOpMap,\n"
         "                    actions = actions\n"
         "                )\n"
         "            }\n"
         "        } else {\n"
         "        ActionsLayout(\n", 1),
        ("            accountCapes = profileUiState.accountCapeOpMap,\n            actions = actions\n        )\n    }\n\n    LoginMenuOperation(",
         "            accountCapes = profileUiState.accountCapeOpMap,\n            actions = actions\n        )\n        }\n    }\n\n    LoginMenuOperation(", 1),
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
# ---- safety: remove duplicate imports (Kotlin refuses the same class imported twice) ----
for _root, _dirs, _files in os.walk(M + "/java"):
    for _fn in _files:
        if not _fn.endswith(".kt"):
            continue
        _p = os.path.join(_root, _fn)
        _lines = open(_p, encoding="utf-8").read().split("\n")
        _seen, _out, _changed = set(), [], False
        for _l in _lines:
            if _l.startswith("import "):
                if _l.strip() in _seen:
                    _changed = True
                    continue
                _seen.add(_l.strip())
            _out.append(_l)
        if _changed:
            open(_p, "w", encoding="utf-8").write("\n".join(_out))

print("CxdElite branding applied. [script v2: duplicate-import fix included]")
