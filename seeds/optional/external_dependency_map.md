# external_dependency_map.md

Tracks all external tools, binaries, scripts, and packages Will relies on.
This allows for self-diagnosis, repair routines, platform-aware logic, and future optimization.

---

## 🧰 Dependency Records

### ffmpeg
```yaml
name: ffmpeg
description: Multimedia framework for video/audio processing
category: binary
use_case: video to audio | stream extraction | screenshot
paths:
  linux: /usr/bin/ffmpeg
  mac: /opt/homebrew/bin/ffmpeg
  windows: C:\ffmpeg\bin\ffmpeg.exe
version_required: 4.3.1+
install_cmd: sudo apt install ffmpeg
health_check: ffmpeg -version
recovery:
  steps:
    - check path
    - reinstall with install_cmd
    - run health_check
  escalation_if_fail: notify_admin
checksum_sha256: <optional SHA>
verify_signature: false
used_by:
  - audio_extraction_reflex
  - video_convert_plugin
usage_stats:
  last_used: 2025-06-26
  frequency_score: high
replacement_options:
  - name: avconv
    type: binary
    notes: ffmpeg fork
```

---

### tesseract
```yaml
name: tesseract
description: OCR engine used for image → text conversion
category: binary
use_case: OCR | scanned docs
paths:
  linux: /usr/bin/tesseract
  mac: /opt/homebrew/bin/tesseract
  windows: C:\Program Files\Tesseract-OCR\tesseract.exe
version_required: 5.0+
install_cmd: sudo apt install tesseract-ocr
health_check: tesseract --version
recovery:
  steps:
    - check path
    - reinstall with install_cmd
    - validate with test_image.png
  escalation_if_fail: quarantine_reflex + log issue
checksum_sha256: <optional SHA>
verify_signature: true
used_by:
  - extract_text_reflex
  - image_ocr_module
usage_stats:
  last_used: 2025-06-25
  frequency_score: medium
replacement_options:
  - name: pytesseract
    type: python_package
    notes: Python fallback with some limitations
```

---

### chromedriver
```yaml
name: chromedriver
description: Headless browser driver for web scraping
category: binary
use_case: crawl | scrape | automated browsing
paths:
  linux: /usr/bin/chromedriver
  mac: /opt/homebrew/bin/chromedriver
  windows: C:\WebDrivers\chromedriver.exe
version_required: 114+
install_cmd: wget + unzip from chromium release page
health_check: chromedriver --version
recovery:
  steps:
    - download latest
    - replace existing binary
    - restart reflex that failed
  escalation_if_fail: fallback_to_http_scraper
checksum_sha256: <optional SHA>
verify_signature: false
used_by:
  - web_crawl_reflex
  - headless_browser_plugin
usage_stats:
  last_used: 2025-06-24
  frequency_score: high
replacement_options:
  - name: playwright
    type: node_module
    notes: Alternative browser automation tool
```

---

### docker
```yaml
name: docker
description: Containerization engine for running isolated services
category: cli_tool
use_case: run models | isolate plugins | test environments
paths:
  linux: /usr/bin/docker
  mac: /opt/homebrew/bin/docker
  windows: C:\Program Files\Docker\docker.exe
version_required: 24.0+
install_cmd: curl | bash (from docker.com)
health_check: docker info
recovery:
  steps:
    - validate daemon is running
    - reinstall from package
    - rerun startup script
  escalation_if_fail: notify_admin + disable container_plugins
checksum_sha256: <optional SHA>
verify_signature: true
used_by:
  - whisper_transcriber
  - model_isolation_reflex
usage_stats:
  last_used: 2025-06-20
  frequency_score: medium
replacement_options:
  - name: podman
    type: cli_tool
    notes: Docker-compatible alternative
```

---

## 🧱 Global Rules

```yaml
allow_partial_dependency_usage: true
platform_aware_pathing: true
auto_version_drift_checks: true
sandbox_degraded_tools: true
log_usage_metrics: true
validate_checksum_on_boot: false
escalate_if_unresolvable: true
```


