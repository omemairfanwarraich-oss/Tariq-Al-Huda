async function loadRecentPdfs() {
    const track = document.getElementById('recent-pdf-track');
    if (!track) return;
    const token = localStorage.getItem('access_token');
    if (!token) {
        track.innerHTML = '<p class="empty-state">Sign in to see your recently opened notes.</p>';
        return;
    }
    const response = await fetch('/api/recent-pdfs', {headers: {Authorization: `Bearer ${token}`} });
    const pdfs = response.ok ? await response.json() : [];
    track.innerHTML = pdfs.length ? pdfs.map((pdf, index) => `<a class="recent-pdf-tile" href="viewer.html?id=${encodeURIComponent(pdf.id)}"><span class="recent-pdf-index">0${index + 1}</span><span class="pdf-badge">PDF · ID ${escapeRecent(pdf.id)}</span><strong>${escapeRecent(pdf.title)}</strong><small>${escapeRecent(pdf.description)}</small><span class="tile-arrow">Open note <b>→</b></span></a>`).join('') : '<p class="empty-state">Open a note and it will appear here.</p>';
}
function escapeRecent(value) { return String(value ?? '').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character])); }
document.addEventListener('DOMContentLoaded', loadRecentPdfs);
