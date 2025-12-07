

// =============================
// 회원정보 수정 화면
// =============================
async function renderProfileEdit() {
  if (!requireLogin()) return;

  app.innerHTML = `
    ${renderHeader()}
    <main class="page profile-page">
      <section class="card" id="profileEditContainer">
        회원정보를 불러오는 중입니다...
      </section>
    </main>
  `;

  bindHeaderEvents();

  try {
    const currentUser = getUser();
    if (!currentUser) {
      alert("로그인이 필요합니다.");
      navigate("#login");
      return;
    }

    const res = await apiRequest(`/users/me?user_id=${currentUser.user_id}`, "GET");
    const data = res.data || res;

    document.getElementById("profileEditContainer").innerHTML = `
      <h2>회원정보 수정</h2>

      <div class="profile-avatar-big">
        ${
          data.profile_image
            ? `<img src="${API_BASE}/${data.profile_image}" class="profile-avatar-big-img" alt="프로필" />`
            : "🙂"
        }
      </div>

      <div class="form-group">
        <label>이메일</label>
        <input type="email" value="${escapeHtml(data.email)}" disabled />
      </div>

      <div class="form-group">
        <label>닉네임</label>
        <input type="text" id="editNickname" value="${escapeHtml(data.nickname || "")}" />
      </div>

      <div class="form-group">
        <label>프로필 사진</label>
        <div class="profile-upload-row">
          <input 
            type="file" 
            id="editProfileImage" 
            class="file-input-hidden" 
            accept="image/*" 
          />
          <label for="editProfileImage" class="secondary-btn file-btn">
            파일 선택
          </label>
          <img 
            id="editProfilePreview" 
            class="profile-edit-preview"
            src="${data.profile_image ? `${API_BASE}/${data.profile_image}` : ""}" 
            alt="미리보기" 
          />
        </div>
      </div>

      <div class="profile-actions">
        <button class="primary-btn" id="btnProfileUpdate">수정하기</button>
        <button class="danger-outline-btn" id="btnDeleteAccount">회원 탈퇴</button>
        <button class="secondary-btn" id="btnProfileDone">수정 완료</button>
      </div>
    `;

    const fileInput = document.getElementById("editProfileImage");
    const previewImg = document.getElementById("editProfilePreview");
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) previewImage(file, previewImg);
    });

    document.getElementById("btnProfileUpdate").addEventListener("click", async () => {
      const nickname = document.getElementById("editNickname").value.trim();
      const nickCheck = validateNickname(nickname);
      if (!nickCheck.ok) {
        alert(nickCheck.msg);
        return;
      }

      const profileFile = fileInput.files[0];

      try {
        const formData = new FormData();
        formData.append("nickname", nickname);
        if (profileFile) {
          formData.append("profile_image", profileFile);
        }

        await apiRequest("/users/me", "PATCH", formData, true);

        // localStorage 갱신
        const user = getUser();
        if (user) {
          user.nickname = nickname;
          saveUser(user);
        }

        alert("회원정보가 수정되었습니다.");
      } catch (e) {}
    });

    document
      .getElementById("btnDeleteAccount")
      .addEventListener("click", () => {
        alert("데모 버전에서는 회원 탈퇴 기능이 구현되어 있지 않습니다.");
      });

    document.getElementById("btnProfileDone").addEventListener("click", () => {
      navigate("#home");
    });
  } catch (e) {
    document.getElementById("profileEditContainer").innerHTML =
      "<p class='error-text'>회원정보를 불러오지 못했습니다.</p>";
  }
}

// =============================
// 비밀번호 수정 화면
// =============================
function renderPasswordEdit() {
  if (!requireLogin()) return;

  app.innerHTML = `
    ${renderHeader()}
    <main class="page password-page">
      <section class="card">
        <h2>비밀번호 수정</h2>

        <div class="form-group">
          <label>새 비밀번호</label>
          <input type="password" id="pwNew" placeholder="8~20자 / 대소문자+숫자+특수문자" />
          <small id="pwNewMsg" class="hint error-text"></small>
        </div>

        <div class="form-group">
          <label>새 비밀번호 확인</label>
          <input type="password" id="pwNewConfirm" placeholder="비밀번호를 다시 입력하세요." />
          <small id="pwConfirmMsg" class="hint error-text"></small>
        </div>

        <button class="primary-btn full" id="btnPwChange">수정하기</button>
      </section>
    </main>
  `;

  bindHeaderEvents();

  const pwNew = document.getElementById("pwNew");
  const pwNewMsg = document.getElementById("pwNewMsg");
  const pwConfirm = document.getElementById("pwNewConfirm");
  const pwConfirmMsg = document.getElementById("pwConfirmMsg");

  pwNew.addEventListener("input", () => {
    const val = pwNew.value;
    if (!val) {
      pwNewMsg.textContent = "비밀번호를 입력해주세요.";
    } else if (!validatePasswordRule(val)) {
      pwNewMsg.textContent =
        "8~20자, 대문자/소문자/숫자/특수문자를 각각 최소 1개 포함해야 합니다.";
    } else {
      pwNewMsg.textContent = "";
    }
  });

  pwConfirm.addEventListener("input", () => {
    const v1 = pwNew.value;
    const v2 = pwConfirm.value;
    if (!v2) {
      pwConfirmMsg.textContent = "비밀번호 확인을 입력해주세요.";
    } else if (v1 !== v2) {
      pwConfirmMsg.textContent = "비밀번호가 일치하지 않습니다.";
    } else {
      pwConfirmMsg.textContent = "";
    }
  });

  document.getElementById("btnPwChange").addEventListener("click", async () => {
    const v1 = pwNew.value;
    const v2 = pwConfirm.value;

    if (!v1) {
      pwNewMsg.textContent = "비밀번호를 입력해주세요.";
      return;
    }
    if (!validatePasswordRule(v1)) {
      pwNewMsg.textContent =
        "8~20자, 대문자/소문자/숫자/특수문자를 각각 최소 1개 포함해야 합니다.";
      return;
    }
    if (!v2) {
      pwConfirmMsg.textContent = "비밀번호 확인을 입력해주세요.";
      return;
    }
    if (v1 !== v2) {
      pwConfirmMsg.textContent = "비밀번호가 일치하지 않습니다.";
      return;
    }

    try {
      const currentUser = getUser();
      await apiRequest(
        `/users/me/password?user_id=${currentUser.user_id}`,
        "PATCH",
        { password: v1 }
      );
      alert("비밀번호가 변경되었습니다. 다시 로그인해주세요.");
      logout();
    } catch (e) {}
  });
}