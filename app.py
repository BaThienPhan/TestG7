import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import csv
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH TRANG & CSS
# ==========================================
st.set_page_config(page_title="Thi Toán 7 Online",
                   layout="wide", page_icon="📐")

st.markdown("""
<style>
    .main-header {font-size: 2rem; color: #4B0082; text-align: center; margin-bottom: 20px;}
    
    /* Tùy chỉnh st.info để làm khung câu hỏi màu xám nhạt thay vì màu xanh mặc định */
    div[data-baseweb="notification"] {
        background-color: #f0f2f6;
        border-left: 5px solid #4B0082;
        color: #1f1f1f;
    }
    
    /* Ẩn icon mặc định của st.info nếu muốn (tùy chọn) */
    div[data-baseweb="notification"] svg {
        display: none;
    }
    
    .stRadio > label {display: none;} /* Ẩn label mặc định của radio */
</style>
""", unsafe_allow_html=True)

FILE_PATH = 'ket_qua_thi_toan7.csv'

# ==========================================
# 2. HÀM VẼ HÌNH (ĐÃ SỬA LỖI CÁI LỀU)
# ==========================================


def draw_tent():
    """
    Vẽ hình lều trại 3D mô phỏng
    Đã bổ sung đường ngang phân cách mái và tường.
    """
    fig, ax = plt.subplots(figsize=(6, 5))

    # Tọa độ mặt trước (Front face)
    # A(0,0), B(4,0), C(4,2), D(0,2), Peak(2, 3.5)
    front_x = [0, 4, 4, 2, 0, 0]
    front_y = [0, 0, 2, 3.5, 2, 0]

    # Vẽ viền mặt trước (ngũ giác)
    ax.plot(front_x, front_y, 'k-', linewidth=2, zorder=10)

    # --- SỬA LỖI: Thêm đường ngang nối D(0,2) và C(4,2) ở mặt trước ---
    ax.plot([0, 4], [2, 2], 'k-', linewidth=2, zorder=10)

    # Vector chiều sâu
    dx, dy = 1.5, 0.8

    # Các điểm mặt sau
    C_back = (4 + dx, 2 + dy)
    Peak_back = (2 + dx, 3.5 + dy)
    B_back = (4 + dx, 0 + dy)
    D_back = (0 + dx, 2 + dy)  # Điểm khuất
    A_back = (0 + dx, 0 + dy)  # Điểm khuất

    # Vẽ các đường nối ra sau (nét liền)
    ax.plot([4, C_back[0]], [2, C_back[1]], 'k-', linewidth=1.5)  # C -> C'
    ax.plot([2, Peak_back[0]], [3.5, Peak_back[1]],
            'k-', linewidth=1.5)  # Đỉnh -> Đỉnh'
    ax.plot([4, B_back[0]], [0, B_back[1]], 'k-', linewidth=1.5)  # B -> B'

    # Vẽ mặt sau (nét liền khung bao nhìn thấy)
    ax.plot([C_back[0], Peak_back[0]], [C_back[1], Peak_back[1]],
            'k-', linewidth=1.5)  # Mái sau phải
    ax.plot([B_back[0], C_back[0]], [B_back[1], C_back[1]],
            'k-', linewidth=1.5)  # Tường sau phải

    # Các đường khuất (nét đứt)
    ax.plot([0, D_back[0]], [2, D_back[1]], 'k--', alpha=0.5)  # D -> D'
    ax.plot([0, A_back[0]], [0, A_back[1]], 'k--', alpha=0.5)  # A -> A'
    ax.plot([A_back[0], B_back[0]], [A_back[1], B_back[1]],
            'k--', alpha=0.5)  # Đáy sau
    ax.plot([A_back[0], D_back[0]], [A_back[1], D_back[1]],
            'k--', alpha=0.5)  # Tường sau trái
    ax.plot([D_back[0], Peak_back[0]], [D_back[1], Peak_back[1]],
            'k--', alpha=0.5)  # Mái sau trái

    # --- SỬA LỖI: Thêm đường ngang khuất ở mặt sau (nối tường và mái sau) ---
    ax.plot([D_back[0], C_back[0]], [D_back[1], C_back[1]], 'k--', alpha=0.5)

    # Chú thích kích thước
    ax.annotate("4m", xy=(2, 0), xytext=(2, -0.3),
                ha='center', fontweight='bold')
    ax.annotate("2m", xy=(0, 1), xytext=(-0.3, 1),
                va='center', fontweight='bold')
    ax.annotate("5m", xy=(4.75, 0.4), xytext=(
        5.2, 0.2), color='blue', fontweight='bold')

    # Đường cao mái
    ax.plot([2, 2], [2, 3.5], 'r--', linewidth=1)
    ax.annotate("1,5m", xy=(2, 2.75), xytext=(
        2.1, 2.75), color='red', fontweight='bold')

    ax.set_title("Mô hình Lều Trại")
    ax.axis('off')
    ax.set_aspect('equal')
    return fig


def draw_pie_chart():
    labels = ['Tốt', 'Khá', 'Đạt', 'Chưa đạt']
    sizes = [25, 45, 20, 10]
    colors = ['#66B2FF', '#FF9999', '#FFFF99', '#99FF99']
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, labels=labels, colors=colors,
           startangle=90, autopct='%1.0f%%')
    ax.set_title("Biểu đồ học lực")
    return fig


def draw_bar_chart():
    months = [7, 8, 9, 10, 11, 12]
    revenue = [40, 50, 45, 60, 85, 90]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(months, revenue, marker='o', color='purple', linewidth=2)
    for i, txt in enumerate(revenue):
        ax.annotate(txt, (months[i], revenue[i]+3), ha='center')
    ax.set_title("Doanh thu 6 tháng cuối năm")
    ax.set_xlabel("Tháng")
    ax.set_ylabel("Triệu đồng")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_ylim(0, 110)
    return fig


def draw_intersecting_lines():
    fig, ax = plt.subplots(figsize=(4, 3))
    x = np.linspace(-2, 2, 100)
    ax.plot(x, -0.6*x, label='xy', color='blue')
    ax.plot(x, 0.6*x, label='zt', color='red')
    ax.text(-1.8, 1, 'x', color='blue')
    ax.text(1.8, -1, 'y', color='blue')
    ax.text(-1.8, -1, 'z', color='red')
    ax.text(1.8, 1, 't', color='red')
    ax.plot(0, 0, 'ko')
    ax.text(0.1, 0.2, 'O')
    ax.axis('off')
    return fig


def draw_angle_bisector():
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.arrow(0, 0, 3, 0, head_width=0.1, color='blue')
    ax.text(3.1, 0, 'x')
    ax.arrow(0, 0, 1, 2.8, head_width=0.1, color='blue')
    ax.text(1, 2.9, 'y')
    ax.arrow(0, 0, 2.4, 1.7, head_width=0.1, color='red')
    ax.text(2.5, 1.7, 'z')
    ax.text(0.2, 0, 'O', ha='right')
    ax.text(1.2, 0.5, r'$35^\circ$', color='red')
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')
    return fig


def draw_parallel_lines():
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.axhline(y=2, color='blue')
    ax.text(4.8, 2.1, 'm', color='blue')
    ax.axhline(y=0, color='blue')
    ax.text(4.8, 0.1, 'n', color='blue')
    ax.plot([0, 0], [-0.5, 2.5], color='black')
    ax.text(-0.3, 2, 'H')
    ax.text(-0.3, 0, 'K')
    ax.add_patch(patches.Rectangle((0, 0), 0.2, 0.2, fill=False))
    ax.plot([1.5, 4.36], [-1.47, 3.5], color='green')
    ax.text(2.2, -0.4, 'E')
    ax.text(3.6, 2.1, 'F')
    ax.text(2.7, 0.3, r'$60^\circ$')
    ax.text(2.9, 1.7, r'$60^\circ$')
    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 3)
    ax.axis('off')
    return fig

# ==========================================
# 3. DỮ LIỆU CÂU HỎI (LATEX RAW STRING)
# ==========================================


questions_mcq = [
    {"q": "Câu 1: Dựa vào bảng kết quả kinh doanh, tháng có mức lỗ nhiều nhất (số lợi nhuận nhỏ nhất) là:", "options": [
        "Tháng 1 (-15,5)", "Tháng 2 (20,1)", "Tháng 3 (-5,8)", "Tháng 4 (-18,2)"], "ans": 3, "table": {"Tháng": ["1", "2", "3", "4"], "Lợi nhuận": [-15.5, 20.1, -5.8, -18.2]}},
    {"q": "Câu 2: Khẳng định nào sau đây là **SAI**?",
        "options": [r"$\sqrt{81} = 9$", r"$|-2,5| = 2,5$", r"$\sqrt{16} \in \mathbb{Q}$", r"$|-5| = -5$"], "ans": 3},
    {"q": r"Câu 3: Kết quả của phép tính $\sqrt{25} \cdot |-4|$ là:",
        "options": ["-20", "20", "1", "-1"], "ans": 1},
    {"q": r"Câu 4: Làm tròn số $76,428$ đến chữ số thập phân thứ nhất ta được:",
        "options": ["76,5", "76,4", "76", "76,43"], "ans": 1},
    {"q": r"Câu 5: Một phòng học hình vuông có diện tích sàn là $64 m^2$. Chu vi của phòng học đó là:",
        "options": ["8 m", "16 m", "32 m", "256 m"], "ans": 2},
    {"q": r"Câu 6: Cho đường thẳng $xy$ cắt đường thẳng $zt$ tại $O$ (Hình vẽ). Góc đối đỉnh với góc $\widehat{xOt}$ là:", "options": [
        r"$\widehat{yOz}$", r"$\widehat{xOz}$", r"$\widehat{yOt}$", r"$\widehat{xOy}$"], "ans": 0, "img_func": draw_intersecting_lines},
    {"q": "Câu 7: Các mặt bên của hình lăng trụ đứng tứ giác là hình gì?", "options": [
        "Hình tam giác", "Hình chữ nhật", "Hình thoi", "Hình bình hành"], "ans": 1},
    {"q": r"Câu 8: Phân số nào dưới đây biểu diễn số hữu tỉ $0,6$?", "options": [
        r"$\frac{3}{5}$", r"$\frac{3}{2}$", r"$\frac{6}{100}$", r"$\frac{1}{6}$"], "ans": 0},
    {"q": "Câu 9: Tiên đề Euclid về đường thẳng song song phát biểu rằng: Qua một điểm ở ngoài một đường thẳng...", "options": [
        "Có vô số đường thẳng song song.", "Có duy nhất một đường thẳng song song.", "Có ít nhất một đường thẳng song song.", "Có hai đường thẳng song song."], "ans": 1},
    {"q": "Câu 10: Trong các dữ liệu sau, dữ liệu nào là **số liệu** (dữ liệu định lượng)?", "options": [
        "Tên các loài động vật trong sách Đỏ.", "Đánh giá hạnh kiểm: Tốt, Khá...", "Chiều cao (cm) của các thành viên.", "Nơi sinh của các bạn trong lớp."], "ans": 2},
    {"q": r"Câu 11: Cho $Oz$ là tia phân giác của $\widehat{xOy}$ (Hình vẽ). Nếu $\widehat{xOz} = 35^\circ$ thì số đo $\widehat{xOy}$ bằng:", "options": [
        r"$35^\circ$", r"$17,5^\circ$", r"$70^\circ$", r"$140^\circ$"], "ans": 2, "img_func": draw_angle_bisector},
    {"q": "Câu 12: Biểu đồ hình quạt tròn biểu diễn học lực (Hình vẽ). Biết tỉ lệ học sinh Khá (Màu Hồng) chiếm nhiều nhất. Màu nào biểu diễn số học sinh Khá?", "options": [
        "Màu Xanh dương", "Màu Hồng", "Màu Vàng", "Màu Xanh lá"], "ans": 1, "img_func": draw_pie_chart},
    {"q": r"Câu 13: Giá trị của biểu thức $A = \frac{3}{7} - 2,5 - \frac{10}{7} + 4,5$ là:",
        "options": ["1", "-1", "2", "0"], "ans": 0},
    {"q": r"Câu 14: Kết quả của $\sqrt{64} - |-2,5| \cdot 4 + \left(\frac{1}{2}\right)^3$ là:", "options": [
        "-1,5", "-1,875", "2,125", "-2"], "ans": 1},
    {"q": r"Câu 15: Tìm $x$, biết $x - \frac{1}{3} = \frac{2}{5}$:",
        "options": [r"$\frac{1}{15}$", r"$\frac{7}{15}$", r"$\frac{11}{15}$", r"$\frac{3}{5}$"], "ans": 2},
    {"q": r"Câu 16: Tìm $x$, biết $\frac{3}{4}x + \frac{1}{2} = \frac{5}{2}$:",
        "options": ["2", r"$\frac{8}{3}$", "4", "3"], "ans": 1},
    {"q": r"Câu 17: Quan sát hình vẽ (2 đường thẳng song song). Mối quan hệ giữa đường thẳng $m$ và $n$ là:", "options": [
        "Cắt nhau", "Song song", "Trùng nhau", "Vuông góc"], "ans": 1, "img_func": draw_parallel_lines},
    {"q": "Câu 18: Quan sát biểu đồ doanh thu bên dưới, xu hướng doanh thu từ tháng 9 đến tháng 12 là:", "options": [
        "Giảm dần", "Không đổi", "Tăng liên tục", "Tăng rồi giảm"], "ans": 2, "img_func": draw_bar_chart},
    {"q": "Câu 19: Quan sát hình vẽ lều trại. Phần mái của chiếc lều trại có dạng hình gì?", "options": [
        "Hình hộp chữ nhật", "Hình chóp tứ giác", "Hình lăng trụ đứng tam giác", "Hình lập phương"], "ans": 2, "img_func": draw_tent},
    {"q": r"Câu 20: (Dựa vào hình vẽ câu 17) Nếu $m // n$ và đường thẳng $HK \perp n$ thì góc tạo bởi $HK$ và $m$ là:",
     "options": [r"$45^\circ$", r"$60^\circ$", r"$90^\circ$", r"$180^\circ$"], "ans": 2}
]

questions_fill = [
    {"q": r"Câu 21: Tìm nghiệm dương của $x$ trong phương trình $|x + 2,5| - 3 = 5$.", "ans": 5.5},
    {"q": r"Câu 22: (Dựa vào hình vẽ câu 17) Tính số đo góc $\widehat{KIE}$ (độ) biết $\widehat{nEF}=60^\circ$, $Kt$ là phân giác góc vuông tại $K$.", "ans": 75},
    {"q": "Câu 23: (Dựa vào biểu đồ doanh thu) Doanh thu cao nhất trong 6 tháng cuối năm là bao nhiêu (triệu đồng)?",
     "ans": 90, "img_func": draw_bar_chart},
    {"q": "Câu 24: Doanh thu tháng 10 tăng bao nhiêu triệu đồng so với tháng 9?", "ans": 15},
    {"q": "Câu 25: Tổng doanh thu của cả 6 tháng cuối năm là bao nhiêu triệu đồng?", "ans": 370},
    {"q": r"Câu 26: (Dựa vào hình vẽ lều trại) Diện tích xung quanh phần tường hình hộp chữ nhật của lều (đáy $4m \times 5m$, cao $2m$) là bao nhiêu $m^2$?",
     "ans": 36, "img_func": draw_tent},
    {"q": r"Câu 27: Tổng diện tích hai tam giác đầu hồi (cạnh đáy $4m$, chiều cao mái $1,5m$) là bao nhiêu $m^2$?", "ans": 6},
    {"q": r"Câu 28: Tổng diện tích vải bạt cần mua sau khi trừ đi $3m^2$ cửa là bao nhiêu $m^2$?", "ans": 39},
    {"q": "Câu 29: Chi phí mua vải bạt là bao nhiêu VNĐ? (Nhập số nguyên, ví dụ 1950000)",
     "ans": 1950000},
    {"q": r"Câu 30: Giá trị của biểu thức $|-2,5| \cdot 4$ là bao nhiêu?", "ans": 10}
]

# ==========================================
# 4. LOGIC HỆ THỐNG
# ==========================================


def save_result(name, correct, total, score):
    file_exists = os.path.isfile(FILE_PATH)
    try:
        with open(FILE_PATH, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(
                    ['Thời gian', 'Họ Tên', 'Số câu đúng', 'Tổng câu', 'Điểm'])
            writer.writerow([datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"), name, correct, total, score])
        return True
    except Exception as e:
        return str(e)


st.sidebar.title("📚 Menu")
page = st.sidebar.radio("Chọn chức năng", ["📝 Làm Bài Thi", "🏆 Bảng Xếp Hạng"])
st.sidebar.markdown("---")
st.sidebar.info("Mã đề: **03** - Thời gian: **90 phút**")

if page == "📝 Làm Bài Thi":
    if 'student_name' not in st.session_state:
        st.markdown("<h1 class='main-header'>🎓 Kiểm Tra Toán 7</h1>",
                    unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### Thông tin học sinh")
            name_input = st.text_input(
                "Nhập Họ và Tên:", placeholder="Ví dụ: Nguyễn Văn A")
            if st.form_submit_button("Bắt Đầu Làm Bài", type="primary"):
                if name_input.strip():
                    st.session_state['student_name'] = name_input
                    st.rerun()
                else:
                    st.error("Vui lòng nhập tên!")
    else:
        student_name = st.session_state['student_name']
        st.markdown(f"### 👋 Xin chào: **{student_name}**")
        st.divider()

        with st.form("exam_form"):
            # --- Phần 1: Trắc Nghiệm ---
            st.header("PHẦN I: TRẮC NGHIỆM (20 câu)")
            user_mcq = {}
            for i, item in enumerate(questions_mcq):
                # SỬ DỤNG ST.INFO ĐỂ HIỂN THỊ LATEX CHÍNH XÁC VÀ CÓ KHUNG MÀU
                st.info(item['q'])

                # Layout Hình ảnh/Bảng biểu
                col_input, col_img = st.columns([2, 1])
                with col_input:
                    if "table" in item:
                        st.dataframe(pd.DataFrame(
                            item['table']), hide_index=True)
                    user_mcq[i] = st.radio(
                        f"Chọn đáp án câu {i+1}", item["options"], index=None, key=f"mcq_{i}")
                with col_img:
                    if "img_func" in item:
                        st.pyplot(item["img_func"](), use_container_width=True)
                st.write("")  # Spacer

            st.divider()

            # --- Phần 2: Điền Khuyết ---
            st.header("PHẦN II: ĐIỀN ĐÁP ÁN (10 câu)")
            st.warning(
                "💡 Lưu ý: Chỉ nhập số (Ví dụ: 5.5 hoặc 10). Không nhập đơn vị.")
            user_fill = {}
            for i, item in enumerate(questions_fill):
                # SỬ DỤNG ST.INFO ĐỂ HIỂN THỊ LATEX
                st.info(item['q'])

                col_input, col_img = st.columns([2, 1])
                with col_input:
                    user_fill[i] = st.number_input(
                        f"Nhập đáp án câu {i+21}:", value=0.0, step=0.1, format="%.4f", key=f"fill_{i}")
                with col_img:
                    if "img_func" in item:
                        st.pyplot(item["img_func"](), use_container_width=True)
                st.write("")

            submit = st.form_submit_button(
                "Nộp Bài", type="primary", use_container_width=True)

        if submit:
            score, total = 0, len(questions_mcq) + len(questions_fill)
            # Chấm điểm
            for i, item in enumerate(questions_mcq):
                if user_mcq[i] == item["options"][item["ans"]]:
                    score += 1
            for i, item in enumerate(questions_fill):
                if abs(user_fill[i] - item["ans"]) < 0.001:
                    score += 1

            final_score = round((score/total)*10, 2)
            st.balloons()
            st.success(f"Đã nộp bài thành công! Điểm: {final_score}/10")

            save_result(student_name, score, total, final_score)

            with st.expander("Xem chi tiết sai sót"):
                for i, item in enumerate(questions_fill):
                    if abs(user_fill[i] - item["ans"]) >= 0.001:
                        st.markdown(f"**Câu {i+21}:** {item['q']}")
                        st.markdown(
                            f"Bạn nhập: `{user_fill[i]}`. Đáp án đúng: `{item['ans']}`")
                        st.divider()

            if st.button("Thoát"):
                del st.session_state['student_name']
                st.rerun()

elif page == "🏆 Bảng Xếp Hạng":
    st.title("🏆 Bảng Xếp Hạng")
    if st.button("Cập nhật"):
        st.rerun()

    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        df = df.sort_values(by="Điểm", ascending=False).reset_index(drop=True)
        df.index += 1
        st.dataframe(df.style.highlight_max(axis=0, subset=[
                     'Điểm'], color='#d4edda'), use_container_width=True)
    else:
        st.info("Chưa có dữ liệu.")
