import { initDemoViewer } from "./AGILE-HOI.github.io/static/js/demo.js";

async function initViewer() {
  const response = await fetch("./assets/site_data.json");
  const siteData = await response.json();
  initDemoViewer({
    containerId: "agile-viewer",
    galleryId: "agile-thumbnail-gallery",
    thumbnailList: siteData.viewerSequences.map((entry) => ({
      label: entry.label,
      thumbnail: entry.thumbnail,
      metadataPath: entry.metadataPath,
    })),
  });
}

initViewer().catch((err) => {
  console.error("Failed to initialize AGILE viewer.", err);
});
