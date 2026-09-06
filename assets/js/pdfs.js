async function loadLibraryPdfs() {
    try {
        const response = await fetch('/api/pdfs');
        if (!response.ok) {
            throw new Error('Failed to fetch PDFs from the backend.');
        }
        
        const pdfs = await response.json();
        const container = document.getElementById('pdf-container');
        
        if (!container) {
            console.error('Element with ID "pdf-container" not found in HTML.');
            return;
        }

        container.innerHTML = '';

        if (pdfs.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No notes available in the library yet.</p>';
            return;
        }

        pdfs.forEach(pdf => {
            const card = document.createElement('div');
            card.className = 'pdf-card';
            card.innerHTML = `
                <h3>${pdf.title}</h3>
                <p>${pdf.description}</p>
                <small style="color: var(--text-muted);">Uploaded: ${pdf.upload_date}</small>
                <div style="margin-top: 15px;">
                    <a href="viewer.html?id=${pdf.id}" class="view-btn">Read Note</a>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading library notes:', error);
    }
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