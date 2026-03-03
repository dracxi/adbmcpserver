---
description: Read Instagram Notifications
---

This workflow automates the process of opening Instagram and reading the latest notifications from the Activity Feed.

1. Open the Instagram application.
// turbo
2. Use `mcp_android-adb_open_app(app_name="instagram")` to launch the app.
3. Wait for the home screen to settle (approx 2-3 seconds).
4. Identify the Notification/Activity icon (Heart) at the top right of the screen.
// turbo
5. Tap the notification icon using `mcp_android-adb_tap(resource_id="com.instagram.android:id/notification")`.
6. Extract all visible notification text.
// turbo
7. Use `mcp_android-adb_read_screen_text()` to capture the list of notifications.
