const goLiveBtn = document.getElementById('go-live-btn');
const streamUrlInput = document.getElementById('stream-url');
const liveVideo = document.getElementById('live-video');
const streamTime = document.getElementById('stream-time');
const uploadInput = document.getElementById('media-upload');
const previewButton = document.getElementById('preview-button');
const publishButton = document.getElementById('publish-button');
const editButtons = document.querySelectorAll('.mini-button');
let isLive = false;

// Go Live button functionality
if (goLiveBtn && streamUrlInput && liveVideo) {
    goLiveBtn.addEventListener('click', () => {
        window.location.href = 'go-live.html';
    });
}

if (uploadInput && previewButton && publishButton) {
    previewButton.addEventListener('click', () => {
        if (uploadInput.files.length === 0) {
            alert('Please choose a video file first.');
            return;
        }
        alert('Video ready for preview. This will open the selected clip in the preview window once connected.');
    });

    publishButton.addEventListener('click', () => {
        if (uploadInput.files.length === 0) {
            alert('Please choose a video to publish.');
            return;
        }
        alert('Your video is prepared for publishing on OwnTube. This panel is a demo workflow.');
    });
}

editButtons.forEach(button => {
    button.addEventListener('click', () => {
        alert('Open the video editor to trim, add captions, and share to TikTok or OwnTube.');
    });
});

