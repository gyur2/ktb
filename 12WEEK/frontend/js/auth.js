// =============================
// 로그인 화면
// =============================
function renderLogin() {
  app.innerHTML = `
    ${renderHeader()}
    <main class="page auth-page">
      <section class="card auth-card">
        <h2>로그인</h2>
        <div class="form-group">
          <label>이메일</label>
          <input type="email" id="loginEmail" placeholder="이메일을 입력하세요." />
        </div>
        <div class="form-group">
          <label>비밀번호</label>
          <input type="password" id="loginPassword" placeholder="비밀번호를 입력하세요." />
        </div>
        <button class="primary-btn full" id="btnLogin">로그인</button>
        <div class="auth-bottom">
          <button class="text-btn" id="goSignup">회원가입</button>
        </div>
      </section>
    </main>
  `;

  bindHeaderEvents();

  document.getElementById("goSignup").addEventListener("click", () => {
    navigate("#signup");
  });

  document.getElementById("btnLogin").addEventListener("click", async () => {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) {
    alert("이메일과 비밀번호를 모두 입력해주세요.");
    return;
  }

  try {
    // 1) 로그인
    const res = await apiRequest("/users/login", "POST", { email, password });
    const loginData = res.data || res;

    // 2) 토큰 저장
    localStorage.setItem("access_token", loginData.access_token);

    // 3) 토큰으로 /users/me에서 프로필 가져오기
    const meRes = await apiRequest("/users/me", "GET");
    const me = meRes.data || meRes;

    saveUser({
      user_id: me.user_id,
      email: me.email,
      nickname: me.nickname,
      profile_image: me.profile_image || null,
    });

    alert("로그인 성공!");
    navigate("#home");
  } catch (e) {
    console.error(e);
  }
});
}

// =============================
// 회원가입 화면
// =============================
function renderSignup() {
  app.innerHTML = `
    ${renderHeader()}
    <main class="page auth-page">
      <section class="card auth-card">
        <h2>회원가입</h2>

        <div class="form-group">
          <label>프로필 사진</label>
          <div class="profile-upload-row">
            <div class="profile-preview-box">
              <img id="signupProfilePreview" class="profile-preview-img" alt="미리보기" />
            </div>
            <div>
              <input 
                type="file" 
                id="signupProfileImage" 
                class="file-input-hidden" 
                accept="image/*" 
              />
              <label for="signupProfileImage" class="secondary-btn file-btn">
                파일 선택
              </label>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>이메일</label>
          <input type="email" id="signupEmail" placeholder="example@email.com" />
          <small class="hint">예) example@example.com</small>
        </div>

        <div class="form-group">
          <label>비밀번호</label>
          <input type="password" id="signupPassword" placeholder="8~20자 / 대소문자+숫자+특수문자" />
        </div>

        <div class="form-group">
          <label>비밀번호 확인</label>
          <input type="password" id="signupPasswordConfirm" placeholder="비밀번호를 다시 입력하세요." />
        </div>

        <div class="form-group">
          <label>닉네임</label>
          <input type="text" id="signupNickname" placeholder="10자 이내, 공백 불가" />
        </div>

        <button class="primary-btn full" id="btnSignup">회원가입</button>

        <div class="auth-bottom" style="margin-top:12px;">
          <button class="secondary-btn full" id="backToLogin">뒤로가기 (로그인)</button>
        </div>
      </section>
    </main>
  `;

  bindHeaderEvents();

  const fileInput = document.getElementById("signupProfileImage");
  const previewImg = document.getElementById("signupProfilePreview");
  let selectedFile = null;

  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      selectedFile = file;
      previewImage(file, previewImg);
      previewImg.style.display = "block";
    }else {
    previewImg.src = "";
    previewImg.style.display = "none"; 
  }
  });

  document.getElementById("backToLogin").addEventListener("click", () => {
    navigate("#login");
  });

  document.getElementById("btnSignup").addEventListener("click", async () => {
    const email = document.getElementById("signupEmail").value.trim();
    const pw = document.getElementById("signupPassword").value;
    const pw2 = document.getElementById("signupPasswordConfirm").value;
    const nickname = document.getElementById("signupNickname").value.trim();
    const profileFile = fileInput.files[0] || null;

    // 필수값 체크
    if (!email || !pw || !pw2 || !nickname) {
      alert("이메일, 비밀번호, 비밀번호 확인, 닉네임을 모두 입력해주세요.");
      return;
    }

    // 이메일 형식 체크
    if (!isValidEmail(email)) {
      alert(
        "올바른 이메일 형식이 아닙니다.\n예) example@example.com 과 같은 형식으로 입력해주세요."
      );
      return;
    }

    // 비밀번호 입력 여부 / 규칙
    if (!pw) {
      alert("비밀번호를 입력해주세요.");
      return;
    }
    if (!validatePasswordRule(pw)) {
      alert(
        "비밀번호 규칙에 맞지 않습니다.\n8~20자, 대문자/소문자/숫자/특수문자를 각각 최소 1개 포함해야 합니다."
      );
      return;
    }

    if (pw !== pw2) {
      alert("비밀번호와 비밀번호 확인이 일치하지 않습니다.");
      return;
    }

    // 닉네임 검사
    const nickCheck = validateNickname(nickname);
    if (!nickCheck.ok) {
      alert(nickCheck.msg);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("password", pw);
      formData.append("nickname", nickname);
      if (profileFile) {
        formData.append("profile_image", profileFile);
      }

      await apiRequest("/users/signup", "POST", formData, true);
      alert("회원가입이 완료되었습니다. 로그인 해주세요.");
      navigate("#login");
    } catch (e) {
      console.error(e);
    }
  });
}
