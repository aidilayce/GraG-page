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
