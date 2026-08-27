(function () {
  const TOP_ROW = [
    { key: "HOLD", label: "HOLD" },
    { key: "BIGS", label: "BIGS" },
    { key: "MagicHOI", label: "MagicHOI" },
  ];
  const BOTTOM_ROW = [
    { key: "Ours", label: "Ours" },
    { key: "GT", label: "Ground-truth" },
  ];

  const comparisonSelectorEl = document.getElementById("comparison-sequence-selector");
  const comparisonViewToggleEl = document.getElementById("comparison-view-toggle");
  const comparisonCameraRowEl = document.getElementById("comparison-camera-row");
  const comparisonSideRowEl = document.getElementById("comparison-side-row");
  const cameraGridTopEl = document.getElementById("comparison-camera-grid-top");
  const cameraGridBottomEl = document.getElementById("comparison-camera-grid-bottom");
  const sideGridTopEl = document.getElementById("comparison-side-grid-top");
  const sideGridBottomEl = document.getElementById("comparison-side-grid-bottom");
  const comparisonCameraTitleEl = document.getElementById("comparison-camera-title");
  const comparisonCameraSubtitleEl = document.getElementById("comparison-camera-subtitle");
  const comparisonSideTitleEl = document.getElementById("comparison-side-title");
  const comparisonSideSubtitleEl = document.getElementById("comparison-side-subtitle");

  function createSequenceCard(entry, clickHandler) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sequence-card";
    button.dataset.key = entry.key;
    button.innerHTML = `
      <img src="${entry.thumbnail}" alt="${entry.label}">
      <div class="sequence-card-body">
        <div class="sequence-card-title">${entry.label}</div>
        ${entry.dataset ? `<div class="sequence-card-dataset">${entry.dataset}</div>` : ""}
      </div>
    `;
    button.addEventListener("click", clickHandler);
    return button;
  }

  function markActive(container, key) {
    container.querySelectorAll(".sequence-card").forEach((card) => {
      card.classList.toggle("active", card.dataset.key === key);
    });
  }

  function configureSegmentVideo(video, clip) {
    const start = clip.start || 0;
    const end = clip.end ?? null;
    const rate = clip.playback_rate || 1.0;
    video.loop = false;
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    video.playbackRate = rate;

    const seekToStart = () => {
      try {
        video.currentTime = start;
      } catch (err) {}
    };

    const restartPlayback = () => {
      seekToStart();
      const playPromise = video.play();
      if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch(() => {});
      }
    };

    video.addEventListener("loadedmetadata", () => {
      restartPlayback();
    });

    video.addEventListener("timeupdate", () => {
      if (end !== null && video.currentTime >= end) {
        restartPlayback();
      }
    });

    video.addEventListener("ended", () => {
      restartPlayback();
    });
  }

  function makeComparisonItem(clip, label) {
    const item = document.createElement("div");
    item.className = "comparison-item";
    if (clip.na || !clip.src) {
      item.innerHTML = `
        <div class="comparison-item-label">${label}</div>
        <div class="comparison-video-frame comparison-video-placeholder">
          <div class="comparison-na">N/A</div>
        </div>
      `;
      return item;
    }
    item.innerHTML = `
      <div class="comparison-item-label">${label}</div>
      <div class="comparison-video-frame">
        <video src="${clip.src}" autoplay muted playsinline controls loop></video>
      </div>
    `;
    configureSegmentVideo(item.querySelector("video"), clip);
    return item;
  }

  function setComparisonView(view) {
    currentView = view;
    comparisonCameraRowEl.classList.toggle("active", view === "camera");
    comparisonSideRowEl.classList.toggle("active", view === "side");
    comparisonViewToggleEl.querySelectorAll(".comparison-view-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.view === view);
    });
  }

  function renderComparisonSequence(entry) {
    markActive(comparisonSelectorEl, entry.key);
    comparisonCameraTitleEl.textContent = entry.title || "Results";
    comparisonCameraSubtitleEl.textContent = entry.camera_subtitle || "";
    comparisonSideTitleEl.textContent = entry.title || "Results";
    comparisonSideSubtitleEl.textContent = entry.side_subtitle || "";

    cameraGridTopEl.innerHTML = "";
    cameraGridBottomEl.innerHTML = "";
    sideGridTopEl.innerHTML = "";
    sideGridBottomEl.innerHTML = "";

    TOP_ROW.forEach((item) => {
      cameraGridTopEl.appendChild(makeComparisonItem(entry.camera[item.key], item.label));
      sideGridTopEl.appendChild(makeComparisonItem(entry.side[item.key], item.label));
    });

    BOTTOM_ROW.forEach((item) => {
      cameraGridBottomEl.appendChild(makeComparisonItem(entry.camera[item.key], item.label));
      sideGridBottomEl.appendChild(makeComparisonItem(entry.side[item.key], item.label));
    });
    setComparisonView(currentView);
  }

  async function init() {
    const response = await fetch("./assets/site_data.json");
    const siteData = await response.json();
    comparisonViewToggleEl.querySelectorAll(".comparison-view-button").forEach((button) => {
      button.addEventListener("click", () => setComparisonView(button.dataset.view));
    });
    siteData.comparisonSequences.forEach((entry) => {
      comparisonSelectorEl.appendChild(
        createSequenceCard(entry, () => renderComparisonSequence(entry))
      );
    });
    if (siteData.comparisonSequences.length > 0) {
      setComparisonView("camera");
      renderComparisonSequence(siteData.comparisonSequences[0]);
    }
  }

  init().catch((err) => {
    console.error("Failed to initialize comparison section.", err);
  });
})();
  let currentView = "camera";

(function () {
  const wrap = document.getElementById("grag-video-wrap");
  if (!wrap) return;

  const video = wrap.querySelector("video");
  const playBtn = wrap.querySelector(".vc-play");
  const bigPlayBtn = wrap.querySelector(".vc-bigplay");
  const seek = wrap.querySelector(".vc-seek");
  const muteBtn = wrap.querySelector(".vc-mute");
  const fsBtn = wrap.querySelector(".vc-fs");
  const timeEl = wrap.querySelector(".vc-time");

  const ICON_PLAY = '<svg viewBox="0 0 24 24"><path d="M8 5.14v13.72L19 12 8 5.14z"></path></svg>';
  const ICON_PAUSE = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path></svg>';
  const ICON_SOUND = '<svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 7.97v8.05A4.47 4.47 0 0 0 16.5 12zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"></path></svg>';
  const ICON_MUTED = '<svg viewBox="0 0 24 24"><path d="M16.5 12A4.5 4.5 0 0 0 14 7.97v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51A8.796 8.796 0 0 0 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3 3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4 9.91 6.09 12 8.18V4z"></path></svg>';

  let scrubbing = false;

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds < 0) return "0:00";
    const total = Math.floor(seconds);
    const mins = Math.floor(total / 60);
    const secs = total % 60;
    return `${mins}:${String(secs).padStart(2, "0")}`;
  }

  function syncTime() {
    timeEl.textContent = `${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;
  }

  function syncProgress() {
    if (scrubbing || !isFinite(video.duration) || video.duration === 0) return;
    const ratio = video.currentTime / video.duration;
    seek.value = String(Math.round(ratio * 1000));
    seek.style.setProperty("--vc-progress", `${ratio * 100}%`);
    syncTime();
  }

  function syncPlayState() {
    const playing = !video.paused && !video.ended;
    playBtn.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
    playBtn.setAttribute("aria-label", playing ? "Pause" : "Play");
    wrap.classList.toggle("is-playing", playing);
    wrap.classList.toggle("controls-visible", !playing);
  }

  function syncMuteState() {
    muteBtn.innerHTML = video.muted ? ICON_MUTED : ICON_SOUND;
    muteBtn.setAttribute("aria-label", video.muted ? "Unmute" : "Mute");
  }

  function togglePlay() {
    if (video.paused || video.ended) {
      const playPromise = video.play();
      if (playPromise && typeof playPromise.catch === "function") {
        // Autoplay policies can reject an unmuted play(); fall back to muted.
        playPromise.catch(() => {
          video.muted = true;
          syncMuteState();
          const retry = video.play();
          if (retry && typeof retry.catch === "function") retry.catch(() => {});
        });
      }
    } else {
      video.pause();
    }
  }

  playBtn.addEventListener("click", togglePlay);
  bigPlayBtn.addEventListener("click", togglePlay);
  video.addEventListener("click", togglePlay);

  video.addEventListener("play", syncPlayState);
  video.addEventListener("pause", syncPlayState);
  video.addEventListener("ended", syncPlayState);
  video.addEventListener("timeupdate", syncProgress);
  video.addEventListener("loadedmetadata", () => {
    syncProgress();
    syncTime();
  });
  video.addEventListener("volumechange", syncMuteState);

  seek.addEventListener("pointerdown", () => {
    scrubbing = true;
  });

  seek.addEventListener("input", () => {
    const ratio = Number(seek.value) / 1000;
    seek.style.setProperty("--vc-progress", `${ratio * 100}%`);
    if (isFinite(video.duration)) {
      timeEl.textContent = `${formatTime(ratio * video.duration)} / ${formatTime(video.duration)}`;
    }
  });

  seek.addEventListener("change", () => {
    if (isFinite(video.duration)) {
      video.currentTime = (Number(seek.value) / 1000) * video.duration;
    }
    scrubbing = false;
  });

  muteBtn.addEventListener("click", () => {
    video.muted = !video.muted;
    syncMuteState();
  });

  fsBtn.addEventListener("click", () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (wrap.requestFullscreen) {
      wrap.requestFullscreen();
    } else if (video.webkitEnterFullscreen) {
      video.webkitEnterFullscreen();
    }
  });

  syncPlayState();
  syncMuteState();
  syncTime();
})();
