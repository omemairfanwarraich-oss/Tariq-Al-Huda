async function loadLibraryPdfs() {
    const container = document.getElementById('pdfGrid');
    if (!container) return;

    try {
        const response = await fetch('/api/pdfs');
        if (!response.ok) {
            throw new Error('Failed to fetch PDFs from the backend.');
        }
        
        const pdfs = await response.json();
        renderLibraryPdfs(pdfs);

        const searchInput = document.getElementById('searchInput');
        const queryFromUrl = new URLSearchParams(window.location.search).get('q');
        if (searchInput && queryFromUrl) searchInput.value = queryFromUrl;
        const applySearch = () => {
            const query = (searchInput?.value || '').trim().toLowerCase();
                renderLibraryPdfs(pdfs.filter(pdf =>
                    `${pdf.id} ${pdf.title} ${pdf.description} ${pdf.file_name || ''}`.toLowerCase().includes(query)
                ));
        };
        if (searchInput) searchInput.addEventListener('input', applySearch);
        document.getElementById('searchButton')?.addEventListener('click', applySearch);
        if (queryFromUrl) applySearch();
    } catch (error) {
        console.error('Error loading library notes:', error);
        container.innerHTML = '<p class="empty-state">Unable to load the library right now.</p>';
    }
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[character]));
}

function renderLibraryPdfs(pdfs) {
    const container = document.getElementById('pdfGrid');
    if (!container) return;

    container.innerHTML = '';
    if (pdfs.length === 0) {
        container.innerHTML = '<p class="empty-state">No notes match your search.</p>';
        return;
    }

    pdfs.forEach(pdf => {
        const card = document.createElement('article');
        card.className = 'pdf-card';
        card.innerHTML = `
            <div class="pdf-card-topline"><span class="pdf-badge">PDF</span><span>${escapeHtml(pdf.upload_date || 'Date unavailable')}</span></div>
            <h2>${escapeHtml(pdf.id)} - ${escapeHtml(pdf.title)}</h2>
            <p>${escapeHtml(pdf.description)}</p>
            <div class="pdf-card-meta">Document ID: ${escapeHtml(pdf.id)}</div>
            <a href="viewer.html?id=${encodeURIComponent(pdf.id)}" class="button button-primary">Open note <span aria-hidden="true">→</span></a>
        `;
        container.appendChild(card);
    });
}

async function postComment(pdfId, message) {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("You must be logged in to comment.");
        window.location.href = "/login.html";
        return;
    }

    try {
        const response = await fetch("/api/discussions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                pdf_id: pdfId,
                message: message
            })
        });

        if (response.ok) {
            // Clear input and reload discussion list if function exists
            if (typeof loadDiscussions === "function") {
                loadDiscussions(pdfId);
            }
        } else {
            const err = await response.json();
            alert(err.detail || "Failed to post comment.");
        }
    } catch (err) {
        console.error("Error posting comment:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadLibraryPdfs);