import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Arc
import math

# 페이지 설정
st.set_page_config(page_title="관측자 위치에 따른 금성 현상 해석", layout="wide", initial_sidebar_state="expanded")

# 제목과 설명
st.title("🌌 관측자 궤도에 따른 금성 현상의 다중 해석")
st.markdown("""
### 태양중심설의 '절대적 증거'는 정말 절대적일까?

**핵심 질문**: 지구가 금성 궤도 **안쪽**에 있다면, 금성의 위상 변화를 천동설로도 설명할 수 있을까?

이 시뮬레이션은 **관측자의 궤도 반지름**을 변경하여 같은 천체 현상이 어떻게 다른 우주관으로 해석될 수 있는지 탐구합니다.
""")

# 사이드바 설정
st.sidebar.header("🎛️ 시뮬레이션 제어")
st.sidebar.markdown("---")

# 관측자(지구) 궤도 반지름 조절 - 핵심 파라미터!
observer_radius = st.sidebar.slider(
    "🌍 관측자 궤도 반지름 (AU)", 
    0.3, 2.0, 1.0, 0.1,
    help="0.72 AU = 금성 궤도, 1.0 AU = 실제 지구 궤도"
)

# 금성은 고정 (0.72 AU)
venus_radius = 0.72
st.sidebar.info(f"🌕 금성 궤도 반지름: {venus_radius} AU (고정)")

# 궤도상 위치
observer_angle = st.sidebar.slider("🌍 관측자 궤도상 위치 (도)", 0, 360, 0, 10)
venus_angle = st.sidebar.slider("🌕 금성 궤도상 위치 (도)", 0, 360, 90, 10)

# 관측 모드
observation_mode = st.sidebar.selectbox(
    "🔭 분석 모드",
    ["통합 분석", "우주 시점", "관측자 시점", "이론 비교"]
)

# 표시 옵션
show_orbits = st.sidebar.checkbox("궤도 표시", True)
show_sun_rays = st.sidebar.checkbox("태양광 표시", True)
show_theory_zones = st.sidebar.checkbox("이론 구분 영역", True)

st.sidebar.markdown("---")

# 궤도 위치에 따른 안내
if observer_radius < venus_radius:
    st.sidebar.warning("⚠️ 관측자가 금성 궤도 **안쪽**에 위치")
    st.sidebar.markdown("→ 천동설 해석 가능성 높음")
elif observer_radius == venus_radius:
    st.sidebar.info("ℹ️ 관측자가 금성과 **같은 궤도**")
    st.sidebar.markdown("→ 특수한 관측 조건")
else:
    st.sidebar.success("✅ 관측자가 금성 궤도 **바깥쪽**에 위치")
    st.sidebar.markdown("→ 지동설의 강력한 증거")

# 물리 계산 함수들
def calculate_positions():
    """관측자와 금성의 위치 계산"""
    observer_x = observer_radius * np.cos(np.radians(observer_angle))
    observer_y = observer_radius * np.sin(np.radians(observer_angle))
    
    venus_x = venus_radius * np.cos(np.radians(venus_angle))
    venus_y = venus_radius * np.sin(np.radians(venus_angle))
    
    return observer_x, observer_y, venus_x, venus_y

def calculate_venus_parameters(observer_x, observer_y, venus_x, venus_y):
    """금성의 모든 관측 파라미터 계산"""
    # 거리 계산
    distance_observer_venus = np.sqrt((observer_x - venus_x)**2 + (observer_y - venus_y)**2)
    distance_sun_venus = np.sqrt(venus_x**2 + venus_y**2)
    distance_sun_observer = np.sqrt(observer_x**2 + observer_y**2)
    
    # 벡터 계산
    sun_venus_vec = np.array([venus_x, venus_y])
    venus_observer_vec = np.array([observer_x - venus_x, observer_y - venus_y])
    sun_observer_vec = np.array([observer_x, observer_y])
    
    # 위상각 (태양-금성-관측자 각도)
    sun_venus_unit = sun_venus_vec / np.linalg.norm(sun_venus_vec)
    venus_observer_unit = venus_observer_vec / np.linalg.norm(venus_observer_vec)
    
    dot_product = np.dot(-sun_venus_unit, venus_observer_unit)
    phase_angle = np.arccos(np.clip(dot_product, -1, 1))
    
    # 조명률 (0~1)
    illuminated_fraction = (1 + np.cos(phase_angle)) / 2
    
    # 각지름 (arctan 근사)
    angular_diameter = 2 * np.arctan(0.006051 / distance_observer_venus)  # 금성 반지름 ≈ 6051km
    
    # 태양-금성-관측자 사이각 (이각)
    # 관측자에서 본 태양-금성 각거리
    sun_observer_unit = sun_observer_vec / np.linalg.norm(sun_observer_vec)
    observer_venus_unit = -venus_observer_unit
    
    elongation_cos = np.dot(sun_observer_unit, observer_venus_unit)
    elongation = np.arccos(np.clip(elongation_cos, -1, 1))
    
    return {
        'phase_angle': phase_angle,
        'illuminated_fraction': illuminated_fraction,
        'angular_diameter': angular_diameter,
        'elongation': elongation,
        'distance_observer_venus': distance_observer_venus,
        'distance_sun_venus': distance_sun_venus,
        'apparent_magnitude': -4.0 + 2.5 * np.log10(distance_observer_venus**2 / illuminated_fraction)
    }

def analyze_theory_compatibility(params, observer_radius):
    """천동설/지동설 호환성 분석"""
    phase_deg = np.degrees(params['phase_angle'])
    elongation_deg = np.degrees(params['elongation'])
    
    # 지동설 호환성 (항상 가능)
    heliocentric_compatible = True
    heliocentric_explanation = "금성이 태양 주위를 공전하므로 모든 위상 관측 가능"
    
    # 천동설 호환성 분석
    geocentric_compatible = False
    geocentric_explanation = ""
    
    if observer_radius < venus_radius:
        # 관측자가 내행성인 경우
        if phase_deg > 90:  # 반달 이상
            geocentric_compatible = True
            geocentric_explanation = "관측자가 금성보다 안쪽에서 태양 주위 공전 → 천동설적 설명 가능"
        else:
            geocentric_explanation = "초승달 위상만 관측 → 천동설 예측과 일치하지만 우연의 일치"
    
    elif observer_radius > venus_radius:
        # 관측자가 외행성인 경우 (실제 지구)
        if phase_deg > 90:  # 반달 이상 위상 관측시
            geocentric_explanation = "천동설로는 설명 불가 → 금성이 태양 너머에 있어야 함"
        else:
            geocentric_explanation = "초승달만 관측 → 천동설 예측과 일치"
    
    else:
        # 같은 궤도
        geocentric_explanation = "특수 조건: 금성과 같은 궤도"
    
    return {
        'heliocentric_compatible': heliocentric_compatible,
        'heliocentric_explanation': heliocentric_explanation,
        'geocentric_compatible': geocentric_compatible,
        'geocentric_explanation': geocentric_explanation
    }

# 계산 실행
observer_x, observer_y, venus_x, venus_y = calculate_positions()
venus_params = calculate_venus_parameters(observer_x, observer_y, venus_x, venus_y)
theory_analysis = analyze_theory_compatibility(venus_params, observer_radius)

# 메인 시각화
if observation_mode == "통합 분석":
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.subheader("🌌 태양계 시뮬레이션")
        fig1, ax1 = plt.subplots(figsize=(10, 10))
        
        # 태양
        sun = Circle((0, 0), 0.08, color='gold', zorder=10, edgecolor='orange', linewidth=2)
        ax1.add_patch(sun)
        
        # 이론 구분 영역
        if show_theory_zones:
            # 금성 궤도 안쪽 (천동설 가능 영역)
            inner_zone = Circle((0, 0), venus_radius, alpha=0.1, color='red', zorder=1)
            ax1.add_patch(inner_zone)
            ax1.text(0.3, 0.3, '천동설\n해석 가능\n영역', ha='center', va='center', 
                    fontsize=10, alpha=0.7, color='red', weight='bold')
            
            # 금성 궤도 바깥쪽 (지동설 강력 증거 영역)
            outer_zone = Circle((0, 0), 2.0, alpha=0.05, color='blue', zorder=0)
            ax1.add_patch(outer_zone)
            ax1.text(1.3, 1.3, '지동설\n강력 증거\n영역', ha='center', va='center', 
                    fontsize=10, alpha=0.7, color='blue', weight='bold')
        
        # 궤도
        if show_orbits:
            observer_orbit = Circle((0, 0), observer_radius, fill=False, color='blue', 
                                  alpha=0.6, linestyle='--', linewidth=2)
            venus_orbit = Circle((0, 0), venus_radius, fill=False, color='orange', 
                               alpha=0.6, linestyle='--', linewidth=2)
            ax1.add_patch(observer_orbit)
            ax1.add_patch(venus_orbit)
        
        # 태양광
        if show_sun_rays:
            for angle in range(0, 360, 30):
                x_end = 2.2 * np.cos(np.radians(angle))
                y_end = 2.2 * np.sin(np.radians(angle))
                ax1.plot([0, x_end], [0, y_end], 'yellow', alpha=0.2, linewidth=0.5)
        
        # 행성
        observer_planet = Circle((observer_x, observer_y), 0.06, color='blue', zorder=10,
                               edgecolor='darkblue', linewidth=1)
        venus_planet = Circle((venus_x, venus_y), 0.05, color='orange', zorder=10,
                            edgecolor='darkorange', linewidth=1)
        ax1.add_patch(observer_planet)
        ax1.add_patch(venus_planet)
        
        # 관측선과 거리 표시
        ax1.plot([observer_x, venus_x], [observer_y, venus_y], 'red', linewidth=2, alpha=0.8)
        
        # 거리 라벨
        mid_x, mid_y = (observer_x + venus_x)/2, (observer_y + venus_y)/2
        ax1.text(mid_x + 0.1, mid_y + 0.1, f'{venus_params["distance_observer_venus"]:.3f} AU', 
                fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 이각 표시 (관측자에서 본 태양-금성 각도)
        if venus_params['elongation'] > 0.1:  # 10도 이상일 때만 표시
            elongation_arc = Arc((observer_x, observer_y), 0.3, 0.3, 
                               angle=0, theta1=0, 
                               theta2=np.degrees(venus_params['elongation']),
                               color='purple', linewidth=2)
            ax1.add_patch(elongation_arc)
            ax1.text(observer_x + 0.2, observer_y + 0.15, f"이각: {np.degrees(venus_params['elongation']):.1f}°", 
                    fontsize=8, color='purple', weight='bold')
        
        ax1.set_xlim(-2.2, 2.2)
        ax1.set_ylim(-2.2, 2.2)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f"관측자 궤도 반지름: {observer_radius:.1f} AU")
        
        # 라벨
        ax1.text(observer_x + 0.08, observer_y + 0.08, '관측자', fontsize=10, weight='bold', color='blue')
        ax1.text(venus_x + 0.08, venus_y + 0.08, '금성', fontsize=10, weight='bold', color='orange')
        ax1.text(0.05, 0.05, '태양', fontsize=10, weight='bold', color='gold')
        
        st.pyplot(fig1)
    
    with col2:
        st.subheader("🔭 관측된 금성")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        
        # 금성 위상 그리기
        venus_display_size = 0.4
        
        # 금성 원판 (어두운 부분)
        venus_disc = Circle((0, 0), venus_display_size, color='#2c2c2c', zorder=5)
        ax2.add_patch(venus_disc)
        
        # 조명받는 부분 계산 및 표시
        if venus_params['illuminated_fraction'] > 0:
            # 태양 방향 각도 (금성에서 본)
            sun_angle = np.degrees(np.arctan2(-venus_y, -venus_x))
            
            # 위상에 따른 조명 영역
            if venus_params['illuminated_fraction'] < 0.5:
                # 초승달 형태
                theta_span = np.degrees(np.arccos(2 * venus_params['illuminated_fraction'] - 1))
                illuminated_wedge = Wedge((0, 0), venus_display_size,
                                        sun_angle - theta_span/2,
                                        sun_angle + theta_span/2,
                                        facecolor='wheat', zorder=6)
            else:
                # 반달 이상
                theta_span = 180 - np.degrees(np.arccos(2 * venus_params['illuminated_fraction'] - 1))
                illuminated_wedge = Wedge((0, 0), venus_display_size,
                                        sun_angle - theta_span/2,
                                        sun_angle + theta_span/2,
                                        facecolor='wheat', zorder=6)
            ax2.add_patch(illuminated_wedge)
        
        # 위상 이름 결정
        phase_deg = np.degrees(venus_params['phase_angle'])
        if phase_deg < 45:
            phase_name = "신월 (New)"
        elif phase_deg < 90:
            phase_name = "초승달 (Crescent)"
        elif phase_deg < 135:
            phase_name = "반달 (Quarter)"
        elif phase_deg < 180:
            phase_name = "보름달에 가까움 (Gibbous)"
        else:
            phase_name = "보름달 (Full)"
        
        ax2.set_xlim(-0.6, 0.6)
        ax2.set_ylim(-0.6, 0.6)
        ax2.set_aspect('equal')
        ax2.set_facecolor('black')
        ax2.set_title(f"위상: {phase_name}", color='white', fontsize=14)
        ax2.set_xticks([])
        ax2.set_yticks([])
        for spine in ax2.spines.values():
            spine.set_visible(False)
        
        st.pyplot(fig2)

elif observation_mode == "이론 비교":
    st.subheader("📚 천동설 vs 지동설 호환성 분석")
    
    # 이론 호환성 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 천동설 (지구중심설)")
        if theory_analysis['geocentric_compatible']:
            st.success("✅ 관측 결과와 호환 가능")
        else:
            st.error("❌ 관측 결과 설명 불가")
        
        st.markdown(f"**설명**: {theory_analysis['geocentric_explanation']}")
        
        # 천동설 예측 시각화
        fig_geo, ax_geo = plt.subplots(figsize=(8, 6))
        
        # 지구 중심 모델 그리기
        earth_center = Circle((0, 0), 0.1, color='blue', zorder=10)
        ax_geo.add_patch(earth_center)
        
        # 금성 궤도 (천동설)
        venus_orbit_geo = Circle((0, 0), 0.5, fill=False, color='orange', linestyle='--')
        ax_geo.add_patch(venus_orbit_geo)
        
        # 태양 궤도 (천동설)
        sun_orbit_geo = Circle((0, 0), 0.8, fill=False, color='yellow', linestyle='-')
        ax_geo.add_patch(sun_orbit_geo)
        
        ax_geo.set_xlim(-1, 1)
        ax_geo.set_ylim(-1, 1)
        ax_geo.set_aspect('equal')
        ax_geo.set_title("천동설 모델")
        ax_geo.text(0, -0.15, "지구", ha='center', fontweight='bold')
        
        st.pyplot(fig_geo)
    
    with col2:
        st.markdown("### ☀️ 지동설 (태양중심설)")
        if theory_analysis['heliocentric_compatible']:
            st.success("✅ 관측 결과와 호환 가능")
        else:
            st.error("❌ 관측 결과 설명 불가")
        
        st.markdown(f"**설명**: {theory_analysis['heliocentric_explanation']}")
        
        # 지동설 예측 시각화
        fig_helio, ax_helio = plt.subplots(figsize=(8, 6))
        
        # 태양 중심 모델
        sun_center = Circle((0, 0), 0.08, color='gold', zorder=10)
        ax_helio.add_patch(sun_center)
        
        # 실제 궤도들
        venus_orbit_helio = Circle((0, 0), venus_radius/1.5, fill=False, color='orange', linestyle='--')
        observer_orbit_helio = Circle((0, 0), observer_radius/1.5, fill=False, color='blue', linestyle='--')
        ax_helio.add_patch(venus_orbit_helio)
        ax_helio.add_patch(observer_orbit_helio)
        
        ax_helio.set_xlim(-1, 1)
        ax_helio.set_ylim(-1, 1)
        ax_helio.set_aspect('equal')
        ax_helio.set_title("지동설 모델")
        ax_helio.text(0, -0.12, "태양", ha='center', fontweight='bold')
        
        st.pyplot(fig_helio)

# 상세 측정값 표시
st.markdown("---")
st.subheader("📊 상세 관측 데이터")

# 메트릭 표시
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("위상각", f"{np.degrees(venus_params['phase_angle']):.1f}°")
    st.caption("태양-금성-관측자 각도")

with col2:
    st.metric("조명률", f"{venus_params['illuminated_fraction']*100:.1f}%")
    st.caption("밝게 보이는 부분 비율")

with col3:
    st.metric("각지름", f"{np.degrees(venus_params['angular_diameter'])*3600:.1f}\"")
    st.caption("하늘에서 보이는 크기")

with col4:
    st.metric("이각", f"{np.degrees(venus_params['elongation']):.1f}°")
    st.caption("태양으로부터 각거리")

with col5:
    st.metric("거리", f"{venus_params['distance_observer_venus']:.3f} AU")
    st.caption("관측자-금성 거리")

# 추가 분석 정보
st.markdown("---")
st.subheader("🔍 핵심 발견사항")

analysis_col1, analysis_col2 = st.columns(2)

with analysis_col1:
    st.markdown("#### 🎯 관측자 위치의 중요성")
    
    if observer_radius < venus_radius:
        st.warning("""
        **현재 상황**: 관측자가 금성 궤도 안쪽에 위치
        
        ⚠️ **주의**: 이 위치에서는 금성의 위상 변화를 천동설로도 설명할 수 있음!
        
        - 금성이 '상급행성'처럼 행동
        - 반달 이상의 위상도 관측 가능
        - 천동설의 '반박 증거'가 약화됨
        """)
    elif observer_radius > venus_radius:
        st.success("""
        **현재 상황**: 관측자가 금성 궤도 바깥쪽에 위치 (실제 지구)
        
        ✅ **결론**: 이 위치에서 금성의 모든 위상을 관측하는 것은 지동설의 강력한 증거
        
        - 천동설로는 반달 이상 위상 설명 불가
        - 갈릴레이의 발견이 혁명적인 이유
        """)
    else:
        st.info("""
        **현재 상황**: 관측자가 금성과 같은 궤도
        
        ℹ️ **특수 조건**: 매우 특별한 관측 조건
        
        - 두 천체가 같은 속도로 공전
        - 상대적 위치 변화 최소화
        """)

with analysis_col2:
    st.markdown("#### 📈 이론별 예측 vs 관측")
    
    # 이론 호환성 요약 테이블
    compatibility_data = {
        "이론": ["천동설", "지동설"],
        "호환성": [
            "✅ 가능" if theory_analysis['geocentric_compatible'] else "❌ 불가능",
            "✅ 가능" if theory_analysis['heliocentric_compatible'] else "❌ 불가능"
        ],
        "핵심 근거": [
            "관측자 위치에 따라 달라짐",
            "모든 궤도에서 설명 가능"
        ]
    }
    
    st.table(compatibility_data)
    
    st.markdown(f"""
    **현재 위상**: {np.degrees(venus_params['phase_angle']):.1f}°
    
    - 90° 미만: 초승달 → 천동설 예측과 일치 가능
    - 90° 이상: 반달 이상 → 관측자가 외부 궤도일 때 천동설 반박
    """)

# 교육적 결론
st.markdown("---")
st.subheader("🎓 철학적 함의")

conclusion_tabs = st.tabs(["과학의 상대성", "관측의 한계", "역사적 맥락", "현대적 의미"])

with conclusion_tabs[0]:
    st.markdown("""
    ### 🌐 과학적 '진리'의 상대성
    
    이 시뮬레이션이 보여주는 핵심:
    
    1. **동일한 현상, 다른 해석**: 금성의 위상 변화라는 같은 현상이 관측자 위치에 따라 다르게 해석될 수 있음
    
    2. **절대적 증거의 한계**: 갈릴레이의 '결정적 증거'는 사실 **지구가 금성 궤도 바깥에 있기 때문**에 가능했음
    
    3. **관측자 중심성**: 과학적 발견이 관측자의 위치와 조건에 의존한다는 상대주의적 관점
    
    **질문**: 만약 지구가 수성 궤도에 있었다면, 우리는 지동설을 발견했을까?
    """)

with conclusion_tabs[1]:
    st.markdown("""
    ### 🔭 관측의 본질적 한계
    
    **관측자 효과의 다층적 의미**:
    
    - **물리적 제약**: 관측자의 공간적 위치가 관측 가능한 현상을 결정
    - **인식론적 한계**: 우리는 우리가 위치한 곳에서만 세상을 볼 수 있음
    - **이론 의존성**: 같은 데이터가 다른 이론적 틀에서 다르게 해석됨
    
    **현대 과학에의 시사점**:
    - 외계행성 관측의 편향
    - 우주론적 관측의 지구 중심성
    - 양자역학의 관측자 문제
    """)

with conclusion_tabs[2]:
    st.markdown("""
    ### 📜 역사적 우연과 필연
    
    **갈릴레이의 행운**:
    - 지구가 '적절한' 위치에 있었기 때문에 지동설 증거 발견 가능
    - 만약 다른 위치였다면 과학 혁명은 어떻게 전개되었을까?
    
    **과학 발전의 우연성**:
    - 관측 기술의 발달 시점
    - 사회적 수용성의 변화
    - 개인의 용기와 통찰력
    
    **반성적 질문**:
    - 현재 우리가 '당연하다'고 생각하는 과학적 사실들 중 얼마나 많은 것이 우리의 특수한 위치 때문일까?
    """)

with conclusion_tabs[3]:
    st.markdown("""
    ### 🚀 현대 과학에의 적용
    
    **외계생명체 탐사**:
    - 지구형 행성 편향: 우리는 지구와 비슷한 조건만 찾고 있지 않은가?
    - 탄소 기반 생명체 가정의 한계
    
    **우주론**:
    - 암흑물질/암흑에너지: 관측 불가능한 것들에 대한 추론의 위험성
    - 다중우주론: 검증 불가능한 이론의 과학성
    
    **인공지능과 인식**:
    - AI의 '객관성': 훈련 데이터의 편향이 반영된 '객관성'
    - 인간 중심적 사고의 한계
    
    **핵심 메시지**: 과학은 절대적 진리가 아닌, 특정 관점에서 본 세상에 대한 최선의 설명
    """)

# 인터랙티브 실험
st.markdown("---")
st.subheader("🧪 직접 실험해보기")

experiment_col1, experiment_col2 = st.columns(2)

with experiment_col1:
    st.markdown("#### 🔬 실험 1: 궤도 위치 변경 실험")
    
    if st.button("🪐 수성 궤도로 이동 (0.39 AU)"):
        st.rerun()
    
    if st.button("🌍 지구 궤도로 이동 (1.0 AU)"):
        st.rerun()
    
    if st.button("🔴 화성 궤도로 이동 (1.52 AU)"):
        st.rerun()
    
    st.markdown("""
    **실험 가이드**:
    1. 각 궤도에서 금성의 위상 변화 관찰
    2. 천동설/지동설 호환성 비교
    3. 이각과 조명률의 상관관계 분석
    """)

with experiment_col2:
    st.markdown("#### 📊 실험 2: 데이터 수집")
    
    # 사용자가 수집할 수 있는 데이터 테이블
    if 'experiment_data' not in st.session_state:
        st.session_state.experiment_data = []
    
    if st.button("📝 현재 데이터 기록"):
        current_data = {
            "궤도 반지름": f"{observer_radius:.2f} AU",
            "위상각": f"{np.degrees(venus_params['phase_angle']):.1f}°",
            "조명률": f"{venus_params['illuminated_fraction']*100:.1f}%",
            "천동설 호환": "O" if theory_analysis['geocentric_compatible'] else "X",
            "지동설 호환": "O" if theory_analysis['heliocentric_compatible'] else "X"
        }
        st.session_state.experiment_data.append(current_data)
    
    if st.session_state.experiment_data:
        st.markdown("**수집된 데이터**:")
        for i, data in enumerate(st.session_state.experiment_data[-5:]):  # 최근 5개만 표시
            st.text(f"{i+1}. R={data['궤도 반지름']}, φ={data['위상각']}, 천동설={data['천동설 호환']}")
    
    if st.button("🗑️ 데이터 초기화"):
        st.session_state.experiment_data = []

# 퀴즈 및 토론 문제
st.markdown("---")
st.subheader("💭 생각해볼 문제들")

quiz_tabs = st.tabs(["기본 이해", "심화 분석", "철학적 토론"])

with quiz_tabs[0]:
    st.markdown("#### 🧩 기본 이해 확인")
    
    q1 = st.radio(
        "Q1. 관측자가 금성 궤도 안쪽에 있을 때, 금성의 반달 이상 위상을 천동설로 설명할 수 있는 이유는?",
        [
            "금성이 지구보다 태양에 가까워서",
            "관측자가 금성을 '상급행성'처럼 볼 수 있어서", 
            "태양이 금성 주위를 돌기 때문에",
            "금성의 자전 때문에"
        ]
    )
    
    if st.button("Q1 정답 확인"):
        if "상급행성" in q1:
            st.success("✅ 정답! 관측자가 안쪽 궤도에 있으면 금성을 외부에서 관찰하게 되어 모든 위상이 가능합니다.")
        else:
            st.error("❌ 다시 생각해보세요. 관측자의 위치가 핵심입니다.")
    
    st.markdown("---")
    
    q2 = st.selectbox(
        "Q2. 갈릴레이의 금성 관측이 '결정적 증거'가 될 수 있었던 핵심 조건은?",
        [
            "망원경의 발명",
            "지구가 금성 궤도 바깥쪽에 위치",
            "금성의 밝기",
            "당시의 사회적 분위기"
        ]
    )
    
    if st.button("Q2 정답 확인"):
        if "바깥쪽" in q2:
            st.success("✅ 정답! 지구의 특수한 위치가 천동설 반박을 가능하게 했습니다.")
        else:
            st.error("❌ 기술이나 사회적 요인보다 물리적 위치가 더 근본적입니다.")

with quiz_tabs[1]:
    st.markdown("#### 🔬 심화 분석 문제")
    
    st.markdown("""
    **분석 과제 1**: 현재 시뮬레이션에서 관측자 궤도를 0.3 AU부터 2.0 AU까지 변경하며 다음을 분석해보세요:
    
    1. 어느 궤도 범위에서 천동설 호환성이 높아지는가?
    2. 이각(elongation)과 위상의 관계는 궤도에 따라 어떻게 변하는가?
    3. 조명률과 각지름의 상관관계를 설명해보세요.
    """)
    
    analysis_input = st.text_area("분석 결과를 작성해주세요:", height=100)
    
    st.markdown("""
    **분석 과제 2**: 만약 금성이 지구보다 바깥쪽 궤도에 있었다면 어떤 일이 일어났을까요?
    
    - 위상 변화 패턴의 차이
    - 천동설/지동설 논쟁에 미칠 영향
    - 과학사의 전개 과정 변화
    """)

with quiz_tabs[2]:
    st.markdown("#### 🤔 철학적 토론 주제")
    
    st.markdown("""
    **토론 주제 1**: 과학적 발견의 우연성
    
    > "만약 지구가 수성 궤도에 있었다면, 인류는 지동설을 발견했을까?"
    
    **찬성 논리**: 
    - 다른 증거들(시차, 수성 위상 등)을 통해 결국 발견했을 것
    - 과학의 누적적 특성상 진리는 결국 밝혀짐
    
    **반대 논리**:
    - 관측 가능한 증거의 부족으로 발견이 늦어졌을 것
    - 초기 조건이 과학 발전 방향을 크게 좌우함
    """)
    
    discussion_input = st.text_area("여러분의 의견을 작성해주세요:", height=80)
    
    st.markdown("""
    **토론 주제 2**: 현대 과학의 '지구 중심성'
    
    > "현재 우리의 과학 이론들 중 얼마나 많은 것이 지구라는 특수한 위치의 편향을 반영하고 있을까?"
    
    **고려 사항**:
    - 외계생명체 탐사의 지구 편향
    - 물리 법칙의 보편성 가정
    - 관측 가능한 우주의 한계
    - 인간 중심적 사고의 한계
    """)

# 추가 학습 자료
st.markdown("---")
st.subheader("📚 심화 학습 자료")

resource_col1, resource_col2 = st.columns(2)

with resource_col1:
    st.markdown("""
    #### 🔗 관련 개념
    
    **천체역학**:
    - 케플러의 법칙과 행성 운동
    - 궤도 역학의 기초
    - 이체 문제와 삼체 문제
    
    **관측천문학**:
    - 시차와 거리 측정
    - 도플러 효과와 적색편이
    - 외계행성 탐지 방법
    
    **과학철학**:
    - 관측자 효과와 상대성
    - 과학적 실재론 vs 반실재론
    - 패러다임 전환 이론
    """)

with resource_col2:
    st.markdown("""
    #### 🎯 실습 확장 아이디어
    
    **시뮬레이션 확장**:
    - 다른 내행성(수성) 추가
    - 시간 변화에 따른 애니메이션
    - 3D 시각화 구현
    
    **데이터 분석**:
    - 위상-거리 상관관계 그래프
    - 궤도별 관측 가능성 매트릭스
    - 통계적 유의성 검증
    
    **역사적 재현**:
    - 갈릴레이의 실제 관측 데이터
    - 브라헤의 화성 관측
    - 케플러의 타원 궤도 발견
    """)

# 결론 및 성찰
st.markdown("---")
st.subheader("🎯 프로젝트 핵심 메시지")

st.success("""
### 🌟 주요 발견사항

1. **상대성의 발견**: 같은 천체 현상도 관측자의 위치에 따라 다르게 해석될 수 있음

2. **우연성의 인식**: 갈릴레이의 '결정적 증거'는 지구가 적절한 위치에 있었기 때문에 가능

3. **편향의 자각**: 현재 우리의 과학적 이해도 지구라는 특수한 관점의 산물일 수 있음

4. **겸손한 자세**: 절대적 진리보다는 최선의 설명을 추구하는 과학의 본질
""")

st.info("""
### 💡 교육적 의의

이 시뮬레이션을 통해 학생들은:
- 과학적 발견의 조건부적 성격을 이해
- 관측과 이론 사이의 복잡한 관계 파악  
- 비판적 사고와 다각적 관점의 중요성 인식
- 현대 과학의 한계와 가능성에 대한 성찰
""")

# 최종 인터랙션
st.markdown("---")
st.markdown("### 🤝 마무리")

final_col1, final_col2 = st.columns(2)

with final_col1:
    if st.button("🔄 시뮬레이션 재시작"):
        st.rerun()
    
    st.markdown("**추천 탐구 순서**:")
    st.markdown("1. 지구 궤도(1.0 AU)에서 기본 관찰")
    st.markdown("2. 금성 궤도 안쪽(0.5 AU)으로 이동")
    st.markdown("3. 화성 궤도(1.5 AU)에서 비교 관찰")
    st.markdown("4. 이론 호환성 변화 분석")

with final_col2:
    st.markdown("**성찰 질문**:")
    reflection = st.text_area(
        "이 시뮬레이션을 통해 과학에 대한 생각이 어떻게 바뀌었나요?",
        height=100,
        placeholder="과학의 객관성, 관측자의 역할, 진리의 상대성 등에 대해 자유롭게 작성해보세요..."
    )

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h4>🌌 금성 위상 시뮬레이션: 관측자 위치의 철학</h4>
    <p><em>"우리가 보는 세상은 우리가 서 있는 곳에 의해 결정된다"</em></p>
    <p><strong>지구과학2 프로젝트 | 태양중심설의 상대적 증거성 탐구</strong></p>
</div>
""", unsafe_allow_html=True)
