// script.js
const grid = document.getElementById("videoGrid");
const loading = document.getElementById("loading");
const searchInput = document.getElementById("searchInput");
const modal = document.getElementById("videoModal");
const player = document.getElementById("videoPlayer");
const videoInfo = document.getElementById("videoInfo");

let allVideos = [];

fetch("/media/list")
  .then(res => res.json())
  .then(videos => {
    allVideos = videos;
    showVideos(videos);
  });

function showVideos(videos) {
  grid.innerHTML = "";
  loading.style.display = "none";
  grid.style.display = "grid";

  videos.forEach(video => {
    const card = document.createElement("div");
    card.className = "video-card";
    card.innerHTML = `
      <div class="video-thumb" style="position:relative;">
        <img src="${video.thumbnail}" alt="${video.title}" />
        <video class="preview" muted preload="none" style="
          display:none; position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; border-radius:8px;">
          <source src="${video.preview}" type="video/mp4">
        </video>
      </div>
      <div class="video-title">${video.title}</div>
    `;
    card.onclick = () => openModal(video.filename);
    card.addEventListener("mouseover", () => {
      const preview = card.querySelector("video.preview");
      preview.style.display = "block";
      preview.currentTime = 0;
      preview.play();
    });
    card.addEventListener("mouseout", () => {
      const preview = card.querySelector("video.preview");
      preview.pause();
      preview.style.display = "none";
    });
    grid.appendChild(card);
  });
}

searchInput.addEventListener("input", e => {
  const keyword = e.target.value.toLowerCase();
  const filtered = allVideos.filter(v => v.title.toLowerCase().includes(keyword));
  showVideos(filtered);
});

function openModal(filename) {
  const video = allVideos.find(v => v.filename === filename);
  if (!video) return;

  player.src = `/videos/${filename}`;
  modal.classList.add("active");

  const meta = video.metadata;
  const stream = meta.streams?.[0] || {};
  const format = meta.format || {};

  const duration = parseFloat(stream.duration || format.duration || 0).toFixed(1);
  const resolution = `${stream.width || "?"} x ${stream.height || "?"}`;
  const codec = stream.codec_name || "Unknown";
  const sizeMB = format.size ? (parseInt(format.size) / (1024 * 1024)).toFixed(1) : "?";
  const bitrate = format.bit_rate ? `${(parseInt(format.bit_rate) / 1000).toFixed(0)} kbps` : "?";

  const audioStream = meta.streams?.find(s => s.codec_type === "audio") || {};
  const audioCodec = audioStream.codec_name || "Unknown";
  const audioChannels = audioStream.channels || "?";

  videoInfo.innerHTML = `
    <h3 style="margin-top:0;">${video.title}</h3>
    <p><strong>Duration:</strong> ${duration} sec</p>
    <p><strong>Resolution:</strong> ${resolution}</p>
    <p><strong>Video Codec:</strong> ${codec}</p>
    <p><strong>Bitrate:</strong> ${bitrate}</p>
    <p><strong>File Size:</strong> ${sizeMB} MB</p>
    <p><strong>Audio:</strong> ${audioCodec}, ${audioChannels} channels</p>
    <button onclick="downloadVideo('${filename}')">⬇ Download</button>
    <button onclick="fullscreenVideo()">⛶ Fullscreen</button>
  `;
}

function closeModal() {
  player.pause();
  modal.classList.remove("active");
  player.src = "";
}

function downloadVideo(filename) {
  const link = document.createElement("a");
  link.href = `/videos/${filename}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function fullscreenVideo() {
  if (player.requestFullscreen) {
    player.requestFullscreen();
  } else if (player.webkitRequestFullscreen) {
    player.webkitRequestFullscreen();
  } else if (player.msRequestFullscreen) {
    player.msRequestFullscreen();
  }
}

// ESC key to close modal
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});
