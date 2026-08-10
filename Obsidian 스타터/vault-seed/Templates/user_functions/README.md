# user_functions

Templater 의 **User Scripts** 폴더입니다. (설정: `Templates/user_functions`)

여기에 `*.js` 파일을 넣으면 템플릿 안에서 `tp.user.<파일명>()` 으로 호출할 수 있습니다.

```js
// 예: today.js
module.exports = async () => {
  return new Date().toLocaleDateString("ko-KR");
};
```

```markdown
<%* tR += await tp.user.today() %>
```

> 스타터에는 개인 계정 자격증명이 필요한 스크립트(구글 캘린더 연동 등)를 넣지 않았습니다.
> 필요하면 각자 추가하세요.
