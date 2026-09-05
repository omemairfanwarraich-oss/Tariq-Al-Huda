// Mock data representing documents that will later be fetched from FastAPI and MongoDB
const mockPdfData = [
    {
        id: "sample-1",
        title: "Introduction to Hadith Sciences",
        category: "Hadith",
        upload_date: "2026-09-06",
        description: "Comprehensive notes covering terminology, classification, and major narrators.",
        file_url: "#"
    },
    {
        id: "sample-2",
        title: "Fundamentals of Islamic Jurisprudence",
        category: "Fiqh",
        upload_date: "2026-09-04",
        description: "An accessible overview of Usool al-Fiqh and primary legal sources.",
        file_url: "#"
    },
    {
        id: "sample-3",
        title: "Tafseer Notes on Surah Al-Kahf",
        category: "Tafseer",
        upload_date: "2026-09-01",
        description: "Detailed linguistic and thematic commentary on the verses of Surah Al-Kahf.",
        file_url: "#"
    }
];

document.addEventListener("DOMContentLoaded", () => {
    const pdfGrid = document.getElementById("pdfGrid");
    const searchInput = document.getElementById("searchInput");

    // Initial render
    renderPdfs(mockPdfData);

    // Event listener for searching
    searchInput.addEventListener("input", filterPdfs);

    function renderPdfs(data) {
        if (data.length === 0) {
            pdfGrid.innerHTML = `<p class="no-results">No PDF notes found matching your search.</p>`;
            return;
        }

        pdfGrid.innerHTML = data.map(pdf => `
            <div class="pdf-card">
                <div class="pdf-card-header">
                    <span class="category-badge">${pdf.category}</span>
                    <span class="date-badge">${pdf.upload_date}</span>
                </div>
                <h3>${pdf.title}</h3>
                <p>${pdf.description}</p>
                <div class="pdf-card-actions">
                    <a href="viewer.html?id=${pdf.id}" class="btn-secondary">Read / View</a>
                    <a href="${pdf.file_url}" class="btn-primary" download>Download PDF</a>
                </div>
            </div>
        `).join("");
    }

    function filterPdfs() {
        const searchTerm = searchInput.value.toLowerCase();

        const filtered = mockPdfData.filter(pdf => {
            return pdf.title.toLowerCase().includes(searchTerm) || 
                pdf.description.toLowerCase().includes(searchTerm) ||
                pdf.category.toLowerCase().includes(searchTerm);
        });

        renderPdfs(filtered);
    }
});