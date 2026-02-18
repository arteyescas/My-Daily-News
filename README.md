# 📻 My Daily News (Automated Spotify Playlist)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-green.svg)
![Spotify](https://img.shields.io/badge/Spotify-API-1DB954.svg)

A Python-based automation tool that curates a personalized "Daily News" playlist on Spotify. 

Every morning at **6:00 AM (Mexico City Time)**, this script fetches the latest episodes from your favorite news podcasts and updates your playlist, ensuring you always have fresh content for your commute or morning routine.

## 🚀 Features

* **Automated Daily Updates:** Runs automatically via GitHub Actions (no server required).
* **Smart Filtering:** Only adds episodes released *today*.
* **Headless Authentication:** Uses Spotify Refresh Tokens to run securely in the cloud without browser interaction.
* **Customizable Sources:** Easily add or remove podcasts by updating the `SHOW_IDS` list.

## 📋 Prerequisites

* A **Spotify Premium** account (required for API playlist modification).
* A **Spotify Developer App** (created via the [Developer Dashboard](https://developer.spotify.com/dashboard)).
* A **GitHub Account** to host the code and run the automation.

---

## 🛠️ Setup Guide

### 1. Spotify Developer Setup
1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2.  Create a new App (e.g., "My Daily News").
3.  **CRITICAL:** Go to **Settings -> User Management** and add your name and the email address associated with your Spotify account. *Without this, the automation will fail with a 403 error.*
4.  Note your **Client ID** and **Client Secret**.
5.  Add `http://127.0.0.1:8080/` (or your chosen URI) to the **Redirect URIs** in Settings.

### 2. Generate Refresh Token
Since GitHub Actions cannot open a browser to log in, you need a one-time **Refresh Token**. 

Run the helper script locally on your computer:
```bash
# Install dependencies
pip install spotipy

# Run generation script (you will need to create this file locally)
python get_refresh_token.py
```
Authorize the app in the browser and copy the `refresh_token` printed in the terminal.

### 3. GitHub Secrets Configuration

To keep your credentials safe, **never** commit them to code. Use GitHub Secrets instead.

1. Go to your Repository **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret** and add the following:

| Secret Name | Value |
| :--- | :--- |
| `SPOTIPY_CLIENT_ID` | Your App's Client ID |
| `SPOTIPY_CLIENT_SECRET` | Your App's Client Secret |
| `SPOTIPY_REDIRECT_URI` | `http://127.0.0.1:8080/` (or whatever you set) |
| `SPOTIPY_REFRESH_TOKEN` | The long string generated in Step 2 |
| `TARGET_PLAYLIST_ID` | The ID of the Spotify Playlist you want to update |

> **Note:** To get the `TARGET_PLAYLIST_ID`, right-click your playlist in Spotify > **Share** > **Copy link to playlist**. The ID is the alphanumeric string after `playlist/`.

## ⚙️ Customization

To change which podcasts are included, edit the `SHOW_IDS` list in `main.py`.

You can find a show's ID by copying its Spotify Link (e.g., `https://open.spotify.com/show/4rOoJ64cGBp78Ko4U56t7n`) and taking the ID part (`4rOoJ64cGBp78Ko4U56t7n`).

```python
SHOW_IDS = [
    "4rOoJ64cGBp78Ko4U56t7n", # Te lo Cuento
    "3zIpqxGvoQkLyySjDq3P95", # Las Noticias del Día MX
    "6o01dGjK3u6GgA36lV6W8f", # Las noticias de la SER
    # Add more IDs here...
]
```

## ⏰ Automation Schedule

The workflow is defined in `.github/workflows/daily_update.yml`.

By default, it runs at **13:00 UTC**, which corresponds to:
* **6:00 AM** in Hermosillo/Mexico City (during Standard Time).

To change the time, edit the cron schedule in the YAML file:

```yaml
on:
  schedule:
    - cron: '0 13 * * *' # Change '13' to your desired UTC hour
```

## ❓ Troubleshooting

**Error: `403 Client Error: Forbidden`**
* **Cause:** Your Spotify App is in "Development Mode" and your email is not whitelisted, OR you are trying to edit a playlist you do not own.
* **Fix:** Go to the Spotify Developer Dashboard -> **Settings** -> **User Management** and ensure your email is listed. Also, ensure the `TARGET_PLAYLIST_ID` belongs to a playlist created by *your* account.

**Error: `The access token expired`**
* **Cause:** The refresh token might be invalid or revoked.
* **Fix:** Regenerate a new Refresh Token locally and update the `SPOTIPY_REFRESH_TOKEN` secret in GitHub.

## 📄 License

This project is for personal use. Enjoy your daily news!
"""
