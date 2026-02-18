# make_readme.py

readme_content = r"""# 📻 My Daily News (Automated Spotify Playlist)

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
5.  Add `http://localhost:8888/callback` (or your chosen URI) to the **Redirect URIs** in Settings.

### 2. Generate Refresh Token
Since GitHub Actions cannot open a browser to log in, you need a one-time **Refresh Token**. 

Run the helper script locally on your computer:
```bash
# Install dependencies
pip install spotipy

# Run generation script (you will need to create this file locally)
python get_refresh_token.py
