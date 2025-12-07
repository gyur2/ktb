
// =============================
// HOME 화면
// =============================
function renderHome() {
  const user = getUser();
  app.innerHTML = `
    ${renderHeader()}
    <main class="page home-page">
      <section class="card upload-card">
        <h2>과즙상 이미지 분류하기 📷</h2>
        <p>과일/야채/얼굴 이미지를 업로드해보세요.</p>
        <div class="upload-wrapper">
          <input type="file" id="homeImageInput" accept="image/*" />
          <div>
            <img id="homeImagePreview" class="image-preview" alt="미리보기"/>
          </div>
          <div>
          <button class="primary-btn full" id="btnPredict">결과 보기</button>
          <div class="result-area" id="predictResult"></div>
          </div>
        </div>
      </section>
    </main>

  `;

  bindHeaderEvents();

  const fileInput = document.getElementById("homeImageInput");
  const preview = document.getElementById("homeImagePreview");
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      previewImage(file, preview);
    }
  });

  document.getElementById("btnPredict").addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
      alert("이미지를 선택해주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const resultBox = document.getElementById("predictResult");
    resultBox.innerHTML = "서버에 요청 중...";

    try {
      const data = await apiRequest("/predict-fruit-veg", "POST", formData, true);
      const probs = data.probabilities || {};
      const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]).slice(0, 5);

      let html = `
        <h3>예측 결과</h3>
        <p><strong>${data.top1_label}</strong> (${(data.top1_score * 100).toFixed(
        2
      )}%)</p>
        <h4>상위 5개 클래스</h4>
        <ul>
          ${sorted
            .map(
              ([label, prob]) =>
                `<li>${escapeHtml(label)} : ${(prob * 100).toFixed(2)}%</li>`
            )
            .join("")}
        </ul>
      `;
      resultBox.innerHTML = html;
    } catch (e) {
      resultBox.innerHTML = "<p class='error-text'>예측에 실패했습니다.</p>";
    }
  });

}