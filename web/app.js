// SanGlow Web Preview - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Play button toggle
    const playBtn = document.querySelector('.play');
    let isPlaying = false;

    playBtn.addEventListener('click', function() {
        isPlaying = !isPlaying;
        this.textContent = isPlaying ? '⏸' : '▶';
    });

    // Quick card click
    const quickCards = document.querySelectorAll('.quick-card');
    quickCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Clicked:', this.textContent);
        });
    });

    // Playlist card click
    const playlistCards = document.querySelectorAll('.playlist-card');
    playlistCards.forEach(card => {
        card.addEventListener('click', function() {
            const name = this.querySelector('.name').textContent;
            console.log('Playing playlist:', name);
        });
    });

    // Volume control
    const volumeSlider = document.querySelector('.volume input[type="range"]');
    volumeSlider.addEventListener('input', function() {
        console.log('Volume:', this.value);
    });

    // Progress slider
    const progressSlider = document.querySelector('.progress input[type="range"]');
    progressSlider.addEventListener('input', function() {
        console.log('Progress:', this.value);
    });
});
