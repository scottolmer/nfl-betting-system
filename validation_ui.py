"""
Streamlit UI for Parlay Validation
Visual interface for validating parlays against DraftKings Pick6 availability
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.prop_availability_validator import PropAvailabilityValidator
from scripts.analysis.parlay_rebuilder import ParlayRebuilder

# Page config
st.set_page_config(
    page_title="Parlay Validator",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'parlays' not in st.session_state:
    st.session_state.parlays = None
if 'analyzed_props' not in st.session_state:
    st.session_state.analyzed_props = None
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = {}
if 'current_parlay_idx' not in st.session_state:
    st.session_state.current_parlay_idx = 0
if 'validator' not in st.session_state:
    st.session_state.validator = PropAvailabilityValidator('bets.db')

# Sidebar
with st.sidebar:
    st.title("🏈 Parlay Validator")
    st.markdown("---")

    # Week selector
    week = st.number_input("Week", min_value=1, max_value=18, value=12)

    # Load data button
    if st.button("📊 Load & Generate Parlays", type="primary", use_container_width=True):
        with st.spinner("Loading data and analyzing props..."):
            try:
                # Load data
                loader = NFLDataLoader(data_dir="data")
                context = loader.load_all_data(week=week)

                # Analyze props
                analyzer = PropAnalyzer()
                analyzed_props = analyzer.analyze_all_props(context, min_confidence=40)
                st.session_state.analyzed_props = analyzed_props

                # Build parlays
                builder = ParlayBuilder()
                parlays = builder.build_parlays(analyzed_props, min_confidence=58)
                st.session_state.parlays = parlays

                # Reset validation state
                st.session_state.validation_results = {}
                st.session_state.current_parlay_idx = 0

                st.success(f"✅ Loaded {len(analyzed_props)} props and built {sum(len(p) for p in parlays.values())} parlays")
                st.rerun()

            except Exception as e:
                st.error(f"Error loading data: {e}")

    st.markdown("---")

    # Statistics
    if st.session_state.parlays:
        st.subheader("📊 Statistics")
        total_parlays = sum(len(p) for p in st.session_state.parlays.values())
        validated = len(st.session_state.validation_results)

        st.metric("Total Parlays", total_parlays)
        st.metric("Validated", validated)
        st.metric("Remaining", total_parlays - validated)

        # Progress bar
        if total_parlays > 0:
            progress = validated / total_parlays
            st.progress(progress)

        # Validation stats
        stats = st.session_state.validator.get_validation_stats()
        st.markdown("---")
        st.caption("**System Stats**")
        st.caption(f"Rules: {stats['total_rules']}")
        st.caption(f"Available props: {stats['props_marked_available']}")
        st.caption(f"Unavailable props: {stats['props_marked_unavailable']}")

# Main content
st.title("🏈 DraftKings Pick6 Parlay Validation")

if st.session_state.parlays is None:
    st.info("👈 Select a week and click 'Load & Generate Parlays' to start")

    st.markdown("---")
    st.subheader("How to Use")
    st.markdown("""
    1. **Select week** in the sidebar
    2. **Load & Generate Parlays** - System will analyze props and build parlays
    3. **Review each parlay** - Check if props are available on DraftKings Pick6
    4. **Mark as Valid or Invalid** - System learns from your feedback
    5. **Rebuild** - System creates new parlays using only valid props
    """)

else:
    # Flatten all parlays into a single list with metadata
    all_parlays = []
    for parlay_type, parlay_list in st.session_state.parlays.items():
        for i, parlay in enumerate(parlay_list):
            all_parlays.append({
                'parlay': parlay,
                'type': parlay_type,
                'index': i + 1
            })

    if len(all_parlays) == 0:
        st.warning("No parlays generated. Try lowering the confidence threshold.")
    else:
        # Check if all parlays are validated
        if len(st.session_state.validation_results) >= len(all_parlays):
            st.success("✅ All parlays validated!")

            # Show rebuild button
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("🔨 Rebuild Parlays with Valid Props", type="primary", use_container_width=True):
                    with st.spinner("Rebuilding parlays..."):
                        # Collect valid props
                        valid_props_pool = []
                        invalid_parlays = []

                        for idx, result in st.session_state.validation_results.items():
                            parlay_data = all_parlays[idx]
                            parlay = parlay_data['parlay']

                            if result['valid']:
                                valid_props_pool.extend(parlay.legs)
                            else:
                                invalid_parlays.append({
                                    'parlay': parlay,
                                    'invalid_props': result.get('invalid_props', [])
                                })

                        # Rebuild
                        rebuilder = ParlayRebuilder('bets.db')

                        # Calculate target counts
                        valid_counts = {'2-leg': 0, '3-leg': 0, '4-leg': 0, '5-leg': 0}
                        for idx, result in st.session_state.validation_results.items():
                            if result['valid']:
                                parlay_data = all_parlays[idx]
                                valid_counts[parlay_data['type']] += 1

                        target_counts = {
                            "2-leg": max(0, 3 - valid_counts.get('2-leg', 0)),
                            "3-leg": max(0, 3 - valid_counts.get('3-leg', 0)),
                            "4-leg": max(0, 3 - valid_counts.get('4-leg', 0)),
                            "5-leg": max(0, 1 - valid_counts.get('5-leg', 0))
                        }

                        new_parlays = rebuilder.rebuild_parlays(
                            valid_props_pool=valid_props_pool,
                            additional_props=st.session_state.analyzed_props,
                            target_counts=target_counts
                        )

                        # Combine valid + rebuilt
                        final_parlays = {}
                        for parlay_type in st.session_state.parlays.keys():
                            valid_of_type = []
                            for idx, result in st.session_state.validation_results.items():
                                if result['valid'] and all_parlays[idx]['type'] == parlay_type:
                                    valid_of_type.append(all_parlays[idx]['parlay'])

                            rebuilt_of_type = new_parlays.get(parlay_type, [])
                            final_parlays[parlay_type] = valid_of_type + rebuilt_of_type

                        st.session_state.parlays = final_parlays
                        st.session_state.validation_results = {}
                        st.session_state.current_parlay_idx = 0

                        st.success(f"✅ Rebuilt parlays! Now showing final validated parlays.")
                        st.rerun()

            with col2:
                if st.button("📊 View Final Parlays", use_container_width=True):
                    st.markdown("---")
                    builder = ParlayBuilder()
                    formatted = builder.format_parlays_for_betting(st.session_state.parlays, "DraftKings Pick6")
                    st.text(formatted)

            # Show validation summary
            st.markdown("---")
            st.subheader("📊 Validation Summary")

            valid_count = sum(1 for r in st.session_state.validation_results.values() if r['valid'])
            invalid_count = len(st.session_state.validation_results) - valid_count

            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Valid Parlays", valid_count)
            col2.metric("❌ Invalid Parlays", invalid_count)
            col3.metric("📦 Props Learned",
                       st.session_state.validator.get_validation_stats()['props_marked_available'] +
                       st.session_state.validator.get_validation_stats()['props_marked_unavailable'])

        else:
            # Get current parlay to validate
            current_idx = st.session_state.current_parlay_idx

            # Skip already validated parlays
            while current_idx < len(all_parlays) and current_idx in st.session_state.validation_results:
                current_idx += 1
                st.session_state.current_parlay_idx = current_idx

            if current_idx >= len(all_parlays):
                st.info("All parlays validated! Click 'Rebuild Parlays' above.")
            else:
                parlay_data = all_parlays[current_idx]
                parlay = parlay_data['parlay']
                parlay_type = parlay_data['type']
                parlay_num = parlay_data['index']

                # Pre-filter with rules
                is_valid_by_rules, violations = st.session_state.validator.validate_parlay_props(parlay.legs)

                if not is_valid_by_rules:
                    # Auto-reject due to rule violations
                    st.error(f"❌ **{parlay_type.upper()} Parlay #{parlay_num}** - RULE VIOLATIONS")
                    for violation in violations:
                        st.warning(violation)

                    st.session_state.validation_results[current_idx] = {
                        'valid': False,
                        'reason': 'Rule violations',
                        'violations': violations
                    }

                    if st.button("⏭️ Next Parlay", type="primary"):
                        st.session_state.current_parlay_idx += 1
                        st.rerun()

                else:
                    # Show parlay for validation
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.subheader(f"📊 {parlay_type.upper()} Parlay #{parlay_num}")

                    with col2:
                        st.metric("Confidence", f"{parlay.combined_confidence}%")

                    st.markdown(f"**{parlay.rationale}**")
                    st.caption(f"Risk Level: {parlay.risk_level}")

                    st.markdown("---")

                    # Display legs with checkboxes
                    st.markdown("### Props")

                    prop_states = {}
                    for i, leg in enumerate(parlay.legs):
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(f"""
                            **{i+1}. {leg.prop.player_name}** ({leg.prop.team}) vs {leg.prop.opponent}
                            - **{leg.prop.stat_type} {leg.prop.bet_type} {leg.prop.line}**
                            - Confidence: {leg.final_confidence}
                            """)

                        with col2:
                            prop_states[i] = st.checkbox(
                                "Available",
                                value=True,
                                key=f"prop_{current_idx}_{i}",
                                label_visibility="visible"
                            )

                    st.markdown("---")

                    # Validation buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("✅ Accept All", type="primary", use_container_width=True):
                            # Mark all props as available
                            for leg in parlay.legs:
                                st.session_state.validator.mark_prop_available(
                                    leg.prop, True, "Validated via UI"
                                )

                            st.session_state.validation_results[current_idx] = {
                                'valid': True,
                                'reason': None
                            }
                            st.session_state.current_parlay_idx += 1
                            st.rerun()

                    with col2:
                        if st.button("❌ Mark Invalid Props", use_container_width=True):
                            # Check which props are unchecked
                            invalid_props = [i for i, available in prop_states.items() if not available]

                            if len(invalid_props) == 0:
                                st.warning("No props marked as unavailable. Use 'Accept All' instead.")
                            else:
                                # Mark props accordingly
                                for i, leg in enumerate(parlay.legs):
                                    if i in invalid_props:
                                        st.session_state.validator.mark_prop_available(
                                            leg.prop, False, "Unavailable on DK Pick6"
                                        )
                                    else:
                                        st.session_state.validator.mark_prop_available(
                                            leg.prop, True, "Available on DK Pick6"
                                        )

                                st.session_state.validation_results[current_idx] = {
                                    'valid': False,
                                    'reason': f"Props {invalid_props} unavailable",
                                    'invalid_props': invalid_props
                                }
                                st.session_state.current_parlay_idx += 1
                                st.rerun()

                    with col3:
                        if st.button("⏭️ Skip", use_container_width=True):
                            st.session_state.current_parlay_idx += 1
                            st.rerun()

                    # Navigation
                    st.markdown("---")
                    st.caption(f"Parlay {current_idx + 1} of {len(all_parlays)}")
