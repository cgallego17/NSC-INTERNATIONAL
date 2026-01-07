/**
 * Debug helper for Vue.js Event Detail App
 * Add this script to check if Vue.js is working correctly
 */

(function() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkVueIntegration);
    } else {
        checkVueIntegration();
    }

    function checkVueIntegration() {
        console.log('=== Vue.js Integration Check ===');

        // Check if Vue is loaded
        if (typeof Vue === 'undefined') {
            console.error('❌ Vue.js is NOT loaded');
            return;
        }
        console.log('✅ Vue.js is loaded:', Vue.version);

        // Check if EventDetailApp is defined
        if (typeof EventDetailApp === 'undefined') {
            console.error('❌ EventDetailApp is NOT defined');
            return;
        }
        console.log('✅ EventDetailApp is defined');

        // Check for Vue app containers
        const appContainers = document.querySelectorAll('[id^="event-detail-app-"]');
        console.log('📦 Vue app containers found:', appContainers.length);

        appContainers.forEach(container => {
            const hotelPk = container.dataset.hotelPk || container.id.replace('event-detail-app-', '');
            console.log(`  - Container for hotel ${hotelPk}:`, container);

            // Check if Vue instance exists
            if (window.VueHotelReservation && window.VueHotelReservation[hotelPk]) {
                console.log(`  ✅ Vue instance found for hotel ${hotelPk}`);
                const instance = window.VueHotelReservation[hotelPk];
                console.log('    Instance properties:', Object.keys(instance));
            } else {
                console.warn(`  ⚠️ Vue instance NOT found for hotel ${hotelPk}`);
            }

            // Check rooms data
            const roomsDataEl = document.getElementById(`rooms-data-${hotelPk}`);
            if (roomsDataEl) {
                try {
                    const roomsData = JSON.parse(roomsDataEl.textContent);
                    console.log(`  ✅ Rooms data found: ${roomsData.length} rooms`);
                } catch (e) {
                    console.error(`  ❌ Error parsing rooms data:`, e);
                }
            } else {
                console.warn(`  ⚠️ Rooms data element NOT found for hotel ${hotelPk}`);
            }
        });

        console.log('=== End Vue.js Integration Check ===');
    }

    // Expose check function globally
    window.checkVueIntegration = checkVueIntegration;
})();

