import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, Arc
import math

# 한글 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title="관측자 위치에 따른 금성 위상 시뮬레이션", layout="wide", initial_sidebar_state="expanded")

# 제목과 설명
st.title("🌌 관측자 위치에 따른 금성 위상 시뮬레이션")
st.markdown("""
### 과학에서 '절대적인 증거'가 존재하는가?

**핵심 질문 : 지구가 현재와 다른 위치에 있었더라도, 금성의 위상이 태양중심설의 절대적인 증거가 되었을까요?**

이 시뮬레이션은 **관측자의 궤도 반지름**을 변경하여 같은 천체 현상이 다른 우주관의 증거로도 해석될 수 있는지 탐구합니다. 
""")



# 사이드바 설정
st.sidebar.header("시뮬레이션 제어")
st.sidebar.markdown("---")

# 궤도 선택 버튼들
st.sidebar.markdown("#### 🪐 빠른 궤도 선택")
col1, col2, col3 = st.sidebar.columns(3)

# 세션 상태 초기화
if 'observer_radius' not in st.session_state:
    st.session_state.observer_radius = 1.0

with col1:
    if st.button("🔴 수성\n0.39 AU", key="mercury"):
        st.session_state.observer_radius = 0.39

with col2:
    if st.button("🌍 지구\n1.0 AU", key="earth"):
        st.session_state.observer_radius = 1.0

with col3:
    if st.button("🔴 화성\n1.52 AU", key="mars"):
        st.session_state.observer_radius = 1.52

st.sidebar.markdown("---")

# 관측자(지구) 궤도 반지름 조절 - 핵심 파라미터!
observer_radius = st.sidebar.slider(
    "🌍 관측자 궤도 반지름 (AU)", 
    0.3, 2.0, st.session_state.observer_radius, 0.1,
    help="0.72 AU = 금성 궤도, 1.0 AU = 실제 지구 궤도"
)

# 세션 상태 업데이트
st.session_state.observer_radius = observer_radius

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
            ax1.text(0.3, 0.3, 'Geocentric\nPossible\nZone', ha='center', va='center', 
                    fontsize=10, alpha=0.7, color='red', weight='bold')
            
            # 금성 궤도 바깥쪽 (지동설 강력 증거 영역)
            outer_zone = Circle((0, 0), 2.0, alpha=0.05, color='blue', zorder=0)
            ax1.add_patch(outer_zone)
            ax1.text(1.3, 1.3, 'Heliocentric\nStrong Evidence\nZone', ha='center', va='center', 
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
            ax1.text(observer_x + 0.2, observer_y + 0.15, f"Elongation: {np.degrees(venus_params['elongation']):.1f}°", 
                    fontsize=8, color='purple', weight='bold')
        
        ax1.set_xlim(-2.2, 2.2)
        ax1.set_ylim(-2.2, 2.2)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f"Observer Orbital Radius: {observer_radius:.1f} AU", fontsize=14)
        
        # 라벨
        ax1.text(observer_x + 0.08, observer_y + 0.08, 'Observer', fontsize=10, weight='bold', color='blue')
        ax1.text(venus_x + 0.08, venus_y + 0.08, 'Venus', fontsize=10, weight='bold', color='orange')
        ax1.text(0.05, 0.05, 'Sun', fontsize=10, weight='bold', color='gold')
        
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
            phase_name = "New"
        elif phase_deg < 90:
            phase_name = "Crescent"
        elif phase_deg < 135:
            phase_name = "Quarter"
        elif phase_deg < 180:
            phase_name = "Gibbous"
        else:
            phase_name = "Full"
        
        ax2.set_xlim(-0.6, 0.6)
        ax2.set_ylim(-0.6, 0.6)
        ax2.set_aspect('equal')
        ax2.set_facecolor('black')
        ax2.set_title(f"Phase: {phase_name}", color='white', fontsize=14)
        ax2.set_xticks([])
        ax2.set_yticks([])
        for spine in ax2.spines.values():
            spine.set_visible(False)
        
        st.pyplot(fig2)

elif observation_mode == "우주 시점":
    st.subheader("🌌 우주에서 본 태양계 전체")
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 태양
    sun = Circle((0, 0), 0.1, color='yellow', zorder=10)
    ax.add_patch(sun)
    
    # 궤도
    if show_orbits:
        observer_orbit = Circle((0, 0), observer_radius, fill=False, color='blue', alpha=0.3, linestyle='--')
        venus_orbit = Circle((0, 0), venus_radius, fill=False, color='orange', alpha=0.3, linestyle='--')
        ax.add_patch(observer_orbit)
        ax.add_patch(venus_orbit)
    
    # 행성
    observer_planet = Circle((observer_x, observer_y), 0.08, color='blue', zorder=10)
    venus_planet = Circle((venus_x, venus_y), 0.06, color='orange', zorder=10)
    ax.add_patch(observer_planet)
    ax.add_patch(venus_planet)
    
    # 태양광 표시
    if show_sun_rays:
        for angle in range(0, 360, 20):
            x_end = 2.2 * np.cos(np.radians(angle))
            y_end = 2.2 * np.sin(np.radians(angle))
            ax.plot([0, x_end], [0, y_end], 'yellow', alpha=0.2, linewidth=0.5)
    
    # 관측선
    ax.plot([observer_x, venus_x], [observer_y, venus_y], 'red', linewidth=2, alpha=0.7)
    ax.text((observer_x + venus_x)/2, (observer_y + venus_y)/2 + 0.1, 
            f'{venus_params["distance_observer_venus"]:.2f} AU', ha='center', fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title("Solar System Configuration", fontsize=16)
    
    # 행성 라벨
    ax.text(observer_x + 0.1, observer_y + 0.1, 'Observer', fontsize=12, fontweight='bold')
    ax.text(venus_x + 0.1, venus_y + 0.1, 'Venus', fontsize=12, fontweight='bold')
    ax.text(0.05, 0.05, 'Sun', fontsize=12, fontweight='bold')
    
    st.pyplot(fig)

elif observation_mode == "관측자 시점":
    st.subheader("🔭 관측자에서 본 금성의 모습")
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 금성의 위상 그리기
    venus_display_size = max(0.4, venus_params['angular_diameter'] * 3)  # 표시용 크기 조정
    
    # 금성 원판 (어두운 부분)
    venus_disc = Circle((0, 0), venus_display_size, color='darkgray', zorder=5)
    ax.add_patch(venus_disc)
    
    # 조명받는 부분의 각도 계산
    # 태양의 방향 벡터 (금성에서 본)
    sun_direction = np.array([-venus_x, -venus_y])
    sun_direction = sun_direction / np.linalg.norm(sun_direction)
    
    # 관측자의 방향 벡터 (금성에서 본)
    observer_direction = np.array([observer_x - venus_x, observer_y - venus_y])
    observer_direction = observer_direction / np.linalg.norm(observer_direction)
    
    # 태양빛이 비치는 방향
    light_angle = np.degrees(np.arctan2(sun_direction[1], sun_direction[0]))
    
    # 조명받는 부분 그리기
    if venus_params['illuminated_fraction'] > 0:
        # 반원 형태의 조명 부분
        theta_range = np.degrees(np.arccos(1 - 2 * venus_params['illuminated_fraction'])) if venus_params['illuminated_fraction'] < 1 else 180
        
        illuminated_wedge = Wedge((0, 0), venus_display_size, 
                                light_angle - theta_range/2, 
                                light_angle + theta_range/2, 
                                facecolor='wheat', zorder=6)
        ax.add_patch(illuminated_wedge)
    
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.set_facecolor('black')
    ax.set_title("Venus as Observed through Telescope", color='white', fontsize=16)
    
    # 격자 제거하고 깔끔하게
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    st.pyplot(fig)

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
        ax_geo.set_title("Geocentric Model")
        ax_geo.text(0, -0.15, "Earth", ha='center', fontweight='bold')
        
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
        ax_helio.set_title("Heliocentric Model")
        ax_helio.text(0, -0.12, "Sun", ha='center', fontweight='bold')
        
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
    
    # 이론 호환성 요약 테이블 (호환성 열 제거)
    compatibility_data = {
        "이론": ["천동설", "지동설"],
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

# 인터랙티브 실험
st.markdown("---")
st.subheader("🧪 직접 실험해보기")

experiment_col1, experiment_col2 = st.columns(2)

with experiment_col1:
    st.markdown("#### 🔬 실험: 궤도 위치 변경")
    
    st.markdown("**추천 실험 순서**:")
    st.markdown("1. **수성 궤도** (0.39 AU): 금성을 '외행성'으로 관측")
    st.markdown("2. **지구 궤도** (1.0 AU): 갈릴레이의 실제 관측 조건")
    st.markdown("3. **화성 궤도** (1.52 AU): 더 멀리서 관측")
    
    st.markdown("""
    **관찰 포인트**:
    - 각 궤도에서 금성 위상 360° 회전시켜 관찰
    - 천동설/지동설 호환성 변화 확인
    - 이각과 조명률의 상관관계 분석
    """)

with experiment_col2:
    st.markdown("#### 📊 실험 기록")
    
    # 사용자가 수집할 수 있는 데이터 기록
    if 'experiment_data' not in st.session_state:
        st.session_state.experiment_data = []
    
    if st.button("📝 현재 상태 기록"):
        current_data = {
            "궤도": f"{observer_radius:.1f} AU",
            "위상": f"{np.degrees(venus_params['phase_angle']):.0f}°",
            "조명률": f"{venus_params['illuminated_fraction']*100:.0f}%",
            "천동설": "O" if theory_analysis['geocentric_compatible'] else "X",
            "지동설": "O" if theory_analysis['heliocentric_compatible'] else "X"
        }
        st.session_state.experiment_data.append(current_data)
        st.success("데이터가 기록되었습니다!")
    
    if st.session_state.experiment_data:
        st.markdown("**기록된 실험 데이터**:")
        for i, data in enumerate(st.session_state.experiment_data[-3:]):  # 최근 3개만 표시
            st.text(f"{i+1}. {data['궤도']} | 위상{data['위상']} | 천동설{data['천동설']}")
    
    if st.button("🗑️ 기록 초기화"):
        st.session_state.experiment_data = []
        st.success("기록이 초기화되었습니다!")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h4>🌌 관측자 위치에 따른 금성 위상 시뮬레이션</h4>
    <p><em>"지구가 현재와 다른 위치에 있었더라도, 금성의 위상이 태양중심설의 절대적인 증거가 되었을까?"</em></p>
    <p><strong>30803 강태원 | 과학에 '절대적 증거'가 존재하는가? </strong></p>
</div>
""", unsafe_allow_html=True)
