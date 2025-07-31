import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(layout="centered")
st.title("💬 인스타 댓글 이미지 생성기")

# ===== 입력 영역 =====
bg_color = st.radio("배경 색상", ["흰색", "검정색"])
nickname = st.text_input("닉네임")
meta = st.text_input("작성일 (예: 2일, 3시간 전 등)")
comment = st.text_area("댓글 내용", height=100)
likes = st.number_input("좋아요 개수", min_value=0, step=1)
uploaded_image = st.file_uploader("프로필 이미지 업로드", type=["png", "jpg", "jpeg"])

# ===== 버튼 클릭 시 =====
if st.button("이미지 만들기") and uploaded_image and nickname and meta and comment:
    # ===== 색상 설정 =====
    bg = (255, 255, 255) if bg_color == "흰색" else (0, 0, 0)
    text_color = (0, 0, 0) if bg_color == "흰색" else (255, 255, 255)
    gray_color = (160, 160, 160)

    # ===== 폰트 설정 =====
    bold_font_path = "assets/Pretendard-Bold.otf"
    medium_font_path = "assets/Pretendard-Medium.otf"
    font_nick = ImageFont.truetype(bold_font_path, 25)        # 닉네임
    font_meta = ImageFont.truetype(medium_font_path, 21)      # 작성일 (회색)
    font_comment = ImageFont.truetype(medium_font_path, 25)   # 댓글
    font_small = ImageFont.truetype(medium_font_path, 19)     # 좋아요+답글 (회색)

    # ===== 간격 설정 =====
    padding_x = 20
    padding_y_top = 18
    padding_y_bottom = 10
    profile_size = 50
    profile_to_text_gap = 14     # 프로필 ↔ 텍스트 X 간격
    nick_to_comment_gap = 8      # 닉네임 ↔ 댓글 Y 간격
    comment_to_likes_gap = 20    # 댓글 ↔ 좋아요 Y 간격
    line_spacing = 1

    text_start_x = padding_x + profile_size + profile_to_text_gap
    max_line_width = 0

    # ===== 줄 나누기 =====
    temp_img = Image.new("RGB", (1000, 1000), bg)
    draw = ImageDraw.Draw(temp_img)
    words = comment.split(" ")
    lines = []
    line = ""
    for word in words:
        test_line = line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font_comment)
        if bbox[2] - bbox[0] < 600:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_comment)
        max_line_width = max(max_line_width, bbox[2])
        line_heights.append(bbox[3] - bbox[1] + line_spacing)
    comment_height = sum(line_heights)

    # 좋아요 줄 너비
    like_text = f"좋아요 {likes}개    답글 달기"
    like_width = draw.textbbox((0, 0), like_text, font=font_small)[2]
    max_line_width = max(max_line_width, like_width)

    # 닉네임+작성일 너비
    nick_width = draw.textbbox((0, 0), nickname, font=font_nick)[2]
    meta_width = draw.textbbox((0, 0), meta, font=font_meta)[2]
    max_line_width = max(max_line_width, nick_width + 10 + meta_width)

    total_width = text_start_x + max_line_width + padding_x
    total_height = (
        padding_y +
        max(profile_size, font_nick.size) +
        nick_to_comment_gap +
        comment_height +
        comment_to_likes_gap +
        font_small.size +
        padding_y
    )

    # ===== 이미지 생성 =====
    img = Image.new("RGB", (total_width, total_height), bg)
    draw = ImageDraw.Draw(img)

    # 프로필
    profile = Image.open(uploaded_image).convert("RGB").resize((profile_size, profile_size))
    mask = Image.new("L", (profile_size, profile_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, profile_size, profile_size), fill=255)
    img.paste(profile, (padding_x, padding_y), mask)

    # 닉네임 + 작성일
    draw.text((text_start_x, padding_y), nickname, font=font_nick, fill=text_color)
    draw.text((text_start_x + nick_width + 10, padding_y + 3), meta, font=font_meta, fill=gray_color)

    # 댓글
    current_y = padding_y + font_nick.size + nick_to_comment_gap
    for line in lines:
        draw.text((text_start_x, current_y), line, font=font_comment, fill=text_color)
        h = draw.textbbox((0, 0), line, font=font_comment)[3] - draw.textbbox((0, 0), line, font=font_comment)[1]
        current_y += h + line_spacing

    # 좋아요 + 답글 달기
    current_y += comment_to_likes_gap
    draw.text((text_start_x, current_y), like_text, font=font_small, fill=gray_color)

    # ===== 출력 및 다운로드 =====
    st.image(img)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("이미지 다운로드", data=buf.getvalue(), file_name="insta_comment.png", mime="image/png")
