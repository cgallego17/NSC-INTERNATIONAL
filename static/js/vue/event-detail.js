/**
 * Vue.js Application for Event Detail Page
 * Replaces the vanilla JavaScript implementation with a more organized Vue.js structure
 */

const { createApp, ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } = Vue;

// ============================================
// Translation Helper
// ============================================

// Use Django's gettext if available, otherwise return key
const gettext = (typeof window !== 'undefined' && typeof window.gettext === 'function')
    ? window.gettext
    : (s) => s;

const translations = {
    selectRoom: gettext('Select Room'),
    sortBy: gettext('Sort by:'),
    default: gettext('Default'),
    recommended: gettext('Recommended'),
    priceLowToHigh: gettext('Price (Low to High)'),
    priceHighToLow: gettext('Price (High to Low)'),
    capacityLowToHigh: gettext('Capacity (Low to High)'),
    capacityHighToLow: gettext('Capacity (High to Low)'),
    people: gettext('people'),
    max: gettext('Max'),
    breakfast: gettext('Breakfast'),
    night: gettext('night'),
    basePriceIncludes: gettext('Base price includes this number of guests'),
    priceIncludes: gettext('Price includes'),
    guest: gettext('guest'),
    guests: gettext('guests'),
    details: gettext('Details'),
    roomDetails: gettext('Room Details'),
    amenities: gettext('Amenities'),
    services: gettext('Services'),
    rules: gettext('Rules'),
    loading: gettext('Loading...'),
    back: gettext('Back'),
    close: gettext('Close'),
    capacityHighToLow: gettext('Capacity (High to Low)'),
    capacity: gettext('Capacity'),
    select: gettext('Select'),
    remove: gettext('Remove'),
    selected: gettext('Selected'),
    rooms: gettext('room(s)'),
    cancel: gettext('Cancel'),
    continue: gettext('Continue'),
    guestDetails: gettext('Guest Details'),
    adults: gettext('Adults'),
    children: gettext('Children'),
    name: gettext('Name'),
    email: gettext('Email'),
    phone: gettext('Phone'),
    birthdate: gettext('Date of Birth'),
    addAdult: gettext('Add Adult'),
    addChild: gettext('Add Child'),
    roomAdded: gettext('Room "{label}" added'),
    roomRemoved: gettext('Room "{label}" removed'),
    guestsAdded: gettext('Guests added successfully'),
    pleaseSelectRoom: gettext('Please select at least one room'),
    pleaseAddGuests: gettext('Please add guest details'),
    priceBreakdown: gettext('Price Breakdown'),
    total: gettext('Total'),
    continueToCheckout: gettext('Continue to Checkout'),
    // Event detail translations
    eventDetails: gettext('Event Details'),
    eventInformationAndRegistration: gettext('Event information and registration'),
    eventInformation: gettext('Event Information'),
    startDate: gettext('Start Date'),
    endDate: gettext('End Date'),
    location: gettext('Location'),
    status: gettext('Status'),
    divisions: gettext('Divisions'),
    showMore: gettext('Show more'),
    showLess: gettext('Show less'),
    headquartersHotel: gettext('Headquarters Hotel'),
    primarySite: gettext('Primary Site'),
    eventVideo: gettext('Event Video'),
    description: gettext('Description'),
    moreInformation: gettext('More Information'),
    checkout: gettext('Checkout'),
    selectPlayers: gettext('Select Players'),
    registered: gettext('Registered'),
    alreadyRegistered: gettext('Already registered'),
    addHotelStay: gettext('Add Hotel Stay'),
    hotelBuyOutFeeMessage: gettext("If you don't add a hotel stay, a Hotel buy out fee will apply."),
    orderSummary: gettext('Order Summary'),
    players: gettext('Player(s)'),
    player: gettext('Player'),
    eventRegistration: gettext('Event registration'),
    loading: gettext('Loading...'),
    // Guest management translations
    addGuest: gettext('Add Guest'),
    yourGuests: gettext('Your Guests'),
    guestsList: gettext('Guests List'),
    noGuestsAdded: gettext('No guests added yet'),
    adult: gettext('Adult'),
    child: gettext('Child'),
    yearsOld: gettext('years old'),
    selectRoomToSeePrice: gettext('Select a room to see price calculation'),
    basePrice: gettext('Base Price'),
    additionalGuests: gettext('Additional Guests'),
    howToProceed: gettext('How to proceed:'),
    reviewGuestsBelow: gettext('Review your guests below (you can add more)'),
    clickRoomToSeeDetails: gettext('Click on a room to see details'),
    clickSelectToChooseRoom: gettext('Click \'Select\' to choose a room'),
    clickContinueWhenReady: gettext('Click \'Continue\' when ready'),
    firstName: gettext('First Name'),
    lastName: gettext('Last Name'),
    guestType: gettext('Guest Type'),
    enterFirstName: gettext('Enter first name'),
    enterLastName: gettext('Enter last name'),
    enterEmailAddress: gettext('Enter email address'),
    dateOfBirth: gettext('Date of Birth'),
    saveGuest: gettext('Save Guest'),
    back: gettext('Back'),
    registrant: gettext('Registrant'),
    availableRooms: gettext('Available Rooms'),
    room: gettext('room'),
    selectRoomToContinue: gettext('Select a room to continue'),
    included: gettext('Included'),
    person: gettext('person'),
    rule: gettext('Rule'),
    roomSize: gettext('Room size'),
    extraLargeBed: gettext('extra-large double bed'),
    per: gettext('per'),
    additionalGuest: gettext('additional guest'),
    roomSize: gettext('Room size'),
    extraLargeBed: gettext('extra-large double bed')
};

// Simple translation function for Vue templates
function $t(key) {
    return translations[key] || key;
}

// ============================================
// Composables / Services
// ============================================

/**
 * Hotel Reservation Service
 * Manages room selection, guest assignment, and price calculation
 */
function useHotelReservation(hotelPk) {
    const state = reactive({
        rooms: [],
        guests: [],
        guestAssignments: {}, // { roomId: [guestIndex1, guestIndex2, ...] }
    });

    const selectedRooms = computed(() => {
        return Array.isArray(state.rooms) ? state.rooms : [];
    });
    const totalGuests = computed(() => state.guests.length);
    const totalCapacity = computed(() => {
        return state.rooms.reduce((sum, room) => sum + (room.capacity || 0), 0);
    });

    function addRoom(roomId, roomLabel, capacity, price, includesGuests, additionalPrice) {
        const roomIdStr = String(roomId);
        const exists = state.rooms.find(r => r.roomId === roomIdStr);
        if (!exists) {
            console.log('Adding room to state:', roomIdStr, { roomLabel, price });
            state.rooms.push({
                roomId: roomIdStr,
                roomLabel: roomLabel || `Room ${roomIdStr}`,
                capacity: capacity || 0,
                price: parseFloat(price || 0),
                priceIncludesGuests: parseInt(includesGuests || 1),
                additionalGuestPrice: parseFloat(additionalPrice || 0)
            });
            state.guestAssignments[roomIdStr] = [];
        } else {
            console.log('Room already exists in state:', roomIdStr);
        }
    }

    function removeRoom(roomId) {
        const roomIdStr = String(roomId);
        const index = state.rooms.findIndex(r => r.roomId === roomIdStr);
        if (index !== -1) {
            console.log('Removing room from state:', roomIdStr);
            state.rooms.splice(index, 1);
            delete state.guestAssignments[roomIdStr];
        }
    }

    function addGuest(guest) {
        state.guests.push(guest);
    }

    function removeGuest(index) {
        state.guests.splice(index, 1);
        // Remove from all room assignments
        Object.keys(state.guestAssignments).forEach(roomId => {
            state.guestAssignments[roomId] = state.guestAssignments[roomId]
                .filter(guestIdx => guestIdx !== index)
                .map(guestIdx => guestIdx > index ? guestIdx - 1 : guestIdx);
        });
    }

    function assignGuestToRoom(guestIndex, roomId) {
        const roomIdStr = String(roomId);
        if (!state.guestAssignments[roomIdStr]) {
            state.guestAssignments[roomIdStr] = [];
        }
        if (!state.guestAssignments[roomIdStr].includes(guestIndex)) {
            state.guestAssignments[roomIdStr].push(guestIndex);
        }
    }

    function unassignGuestFromRoom(guestIndex, roomId) {
        const roomIdStr = String(roomId);
        if (state.guestAssignments[roomIdStr]) {
            const index = state.guestAssignments[roomIdStr].indexOf(guestIndex);
            if (index !== -1) {
                state.guestAssignments[roomIdStr].splice(index, 1);
            }
        }
    }

    function autoDistributeGuests() {
        // Clear all assignments
        Object.keys(state.guestAssignments).forEach(roomId => {
            state.guestAssignments[roomId] = [];
        });

        // Distribute guests across rooms
        let guestIndex = 0;
        state.rooms.forEach(room => {
            const roomId = String(room.roomId);
            const capacity = room.capacity || 0;
            const assigned = state.guestAssignments[roomId] || [];

            while (assigned.length < capacity && guestIndex < state.guests.length) {
                assigned.push(guestIndex);
                guestIndex++;
            }
            state.guestAssignments[roomId] = assigned;
        });
    }

    function clearAll() {
        state.rooms = [];
        state.guests = [];
        state.guestAssignments = {};
    }

    return {
        state,
        selectedRooms,
        totalGuests,
        totalCapacity,
        addRoom,
        removeRoom,
        addGuest,
        removeGuest,
        assignGuestToRoom,
        unassignGuestFromRoom,
        autoDistributeGuests,
        clearAll
    };
}

/**
 * Price Calculation Service
 */
function usePriceCalculation(hotelPk, reservationState) {
    const priceBreakdown = computed(() => {
        let total = 0;
        const breakdown = [];

        reservationState.rooms.forEach(room => {
            const roomId = String(room.roomId);
            const assignedGuests = reservationState.guestAssignments[roomId] || [];
            const basePrice = parseFloat(room.price || 0);
            const includesGuests = parseInt(room.priceIncludesGuests || 0);
            const additionalGuestPrice = parseFloat(room.additionalGuestPrice || 0);

            let roomTotal = basePrice;
            if (assignedGuests.length > includesGuests) {
                const extraGuests = assignedGuests.length - includesGuests;
                roomTotal += extraGuests * additionalGuestPrice;
            }

            total += roomTotal;
            breakdown.push({
                room: room.roomLabel,
                basePrice,
                assignedGuests: assignedGuests.length,
                roomTotal
            });
        });

        return { total, breakdown };
    });

    return {
        priceBreakdown
    };
}

/**
 * Toast Notification Service
 */
function useToast() {
    const toasts = ref([]);

    function show(message, type = 'info', duration = 3000) {
        const id = Date.now();
        toasts.value.push({
            id,
            message,
            type,
            duration
        });

        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }

        return id;
    }

    function removeToast(id) {
        const index = toasts.value.findIndex(t => t.id === id);
        if (index !== -1) {
            toasts.value.splice(index, 1);
        }
    }

    return {
        toasts,
        show,
        removeToast
    };
}

// ============================================
// Components
// ============================================

/**
 * Room Selection Modal Component
 * Improved version with better UI and functionality
 */
const RoomSelectionModal = {
    props: {
        hotelPk: String,
        rooms: Array,
        selectedRooms: Array,
        show: Boolean,
        guests: {
            type: Array,
            default: () => []
        },
        children: {
            type: Array,
            default: () => []
        },
        selectedChildren: {
            type: Array,
            default: () => []
        },
        registrant: {
            type: Object,
            default: null
        }
    },
    emits: ['close', 'select-room', 'remove-room', 'continue', 'add-guest'],
    setup(props, { emit }) {
        const modalContainer = ref(null);
        const detailRoom = ref(null);
        const detailLoading = ref(false);
        const detailError = ref('');
        const detailCache = ref({}); // roomId -> payload
        const detailImageIndex = ref(0);
        const detailAutoPlayTimer = ref(null);
        const isNarrow = ref(typeof window !== 'undefined' ? window.innerWidth < 992 : true);

        // Ensure selectedRooms is always an array
        const safeSelectedRooms = computed(() => {
            const rooms = props.selectedRooms;
            if (!rooms || !Array.isArray(rooms)) {
                return [];
            }
            console.log('safeSelectedRooms computed update. Count:', rooms.length);
            return rooms;
        });

        const selectedRoomIds = computed(() => {
            return safeSelectedRooms.value.map(r => r.roomId);
        });

        const sortBy = ref('recommended'); // 'recommended', 'price-low-high', 'price-high-low', 'capacity-low-high', 'capacity-high-low'
        const roomSlides = ref({}); // Track active slide for each room
        const roomAutoPlayTimers = ref({}); // Track auto-play timers
        const showAddGuestModal = ref(false);

        const safeGuests = computed(() => {
            return Array.isArray(props.guests) ? props.guests : [];
        });

        const safeChildren = computed(() => {
            return Array.isArray(props.children) ? props.children : [];
        });

        const safeSelectedChildren = computed(() => {
            return Array.isArray(props.selectedChildren) ? props.selectedChildren : [];
        });

        const guestsList = computed(() => {
            const allGuests = [];

            // Add registrant first (always included)
            if (props.registrant) {
                const reg = props.registrant;
                let displayName = '';
                if (reg.name && reg.name.trim()) {
                    displayName = reg.name.trim();
                } else if (reg.first_name && reg.last_name) {
                    displayName = `${reg.first_name.trim()} ${reg.last_name.trim()}`;
                } else if (reg.first_name) {
                    displayName = reg.first_name.trim();
                } else if (reg.last_name) {
                    displayName = reg.last_name.trim();
                } else if (reg.username) {
                    displayName = reg.username;
                } else {
                    displayName = 'Registrant';
                }

                allGuests.push({
                    id: `registrant-${reg.id || reg.pk}`,
                    displayName: displayName,
                    type: 'registrant',
                    age: reg.age || (reg.birth_date ? calculateAge(reg.birth_date) : null),
                    birth_date: reg.birth_date,
                    email: reg.email,
                    isRegistrant: true
                });
            }

            // Add selected players/children
            safeSelectedChildren.value.forEach(childId => {
                const child = safeChildren.value.find(c => c.id === childId || c.pk === childId);
                if (child) {
                    // Build display name - try multiple possible fields
                    let displayName = '';
                    if (child.name && child.name.trim()) {
                        displayName = child.name.trim();
                    } else if (child.first_name && child.last_name) {
                        displayName = `${child.first_name.trim()} ${child.last_name.trim()}`;
                    } else if (child.first_name) {
                        displayName = child.first_name.trim();
                    } else if (child.last_name) {
                        displayName = child.last_name.trim();
                    } else if (child.user && child.user.username) {
                        displayName = child.user.username;
                    } else {
                        displayName = `Player ${child.id || child.pk || childId}`;
                    }

                    allGuests.push({
                        id: `player-${child.id || child.pk || childId}`,
                        displayName: displayName,
                        type: 'player',
                        age: child.age || (child.birth_date ? calculateAge(child.birth_date) : null),
                        birth_date: child.birth_date,
                        email: child.email,
                        isPlayer: true
                    });
                }
            });

            // Add manually added guests
            safeGuests.value.forEach((guest, index) => {
                allGuests.push({
                    ...guest,
                    id: guest.id || `guest-${index}`,
                    displayName: guest.first_name && guest.last_name
                        ? `${guest.first_name} ${guest.last_name}`
                        : guest.name || `Guest ${index + 1}`,
                    type: guest.type || guest.guest_type || 'adult',
                    age: guest.age || (guest.birth_date ? calculateAge(guest.birth_date) : null),
                    isPlayer: false
                });
            });

            return allGuests;
        });

        const priceCalculation = computed(() => {
            console.log('Calculating price. Selected rooms count:', safeSelectedRooms.value.length);

            if (safeSelectedRooms.value.length === 0) {
                return { basePrice: 0, additionalGuests: 0, total: 0 };
            }

            let basePrice = 0;
            let additionalGuests = 0;

            // Calculate total guests (registrant + selected players + manually added guests)
            const totalGuestsCount = guestsList.value.length;
            console.log('Total guests for calculation:', totalGuestsCount);

            safeSelectedRooms.value.forEach(selectedRoom => {
                // Use values directly from the selected room object (already has price, capacity etc)
                const price = parseFloat(selectedRoom.price || 0);
                basePrice += price;

                const includedGuests = parseInt(selectedRoom.priceIncludesGuests || 1);
                console.log(`Room: ${selectedRoom.roomLabel}. Price: ${price}. Included: ${includedGuests}`);

                if (totalGuestsCount > includedGuests) {
                    const extra = totalGuestsCount - includedGuests;
                    const additionalPrice = parseFloat(selectedRoom.additionalGuestPrice || 0) * extra;
                    additionalGuests += additionalPrice;
                    console.log(`Adding additional guests cost: ${additionalPrice} (Extra: ${extra})`);
                }
            });

            const total = basePrice + additionalGuests;
            console.log('Final calculation:', { basePrice, additionalGuests, total });

            return {
                basePrice,
                additionalGuests,
                total
            };
        });

        function calculateAge(birthDate) {
            if (!birthDate) return null;
            const today = new Date();
            const birth = new Date(birthDate);
            let age = today.getFullYear() - birth.getFullYear();
            const monthDiff = today.getMonth() - birth.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
                age--;
            }
            return age;
        }

        function handleAddGuest() {
            showAddGuestModal.value = true;
        }

        function handleGuestAdded(guest) {
            emit('add-guest', guest);
            showAddGuestModal.value = false;
        }

        function handleModalScroll() {
            // Ensure modal stays in view
            const modalEl = document.querySelector('.room-selection-modal-fullscreen');
            if (modalEl) {
                modalEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        function scrollToTop() {
            // Scroll to top immediately when modal opens
            window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
            window.scrollTo(0, 0);
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;

            // Force all scrollable containers to top
            const scrollableElements = document.querySelectorAll('*');
            scrollableElements.forEach(el => {
                if (el.scrollTop > 0) {
                    el.scrollTop = 0;
                }
            });

            // Scroll to top of iframe
            if (window.parent && window.parent !== window) {
                try {
                    window.parent.scrollTo({ top: 0, left: 0, behavior: 'instant' });
                    window.parent.scrollTo(0, 0);
                    window.parent.postMessage({
                        type: 'nsc-scroll-to-top',
                        tabId: window.name || 'event-detail'
                    }, window.location.origin);
                } catch (e) {
                    // Cross-origin, can't scroll parent
                }
            }

            // Scroll modal container to top
            if (modalContainer.value) {
                modalContainer.value.scrollTop = 0;
                modalContainer.value.scrollIntoView({ behavior: 'auto', block: 'start' });
                // Force scroll after a tiny delay
                setTimeout(() => {
                    if (modalContainer.value) {
                        modalContainer.value.scrollTop = 0;
                        modalContainer.value.scrollIntoView({ behavior: 'auto', block: 'start' });
                    }
                }, 10);
            }
        }

        // Function to hoist modal to body (for iframe compatibility)
        // NOTE: Do NOT move Vue-managed DOM nodes to window.parent.document; it can break rendering and event handlers.
        function hoistModalToBody() {
            nextTick(() => {
                if (!modalContainer.value) return;

                // Keep modal inside the current document (iframe) but ensure it's attached to <body>
                if (modalContainer.value.parentElement !== document.body) {
                    document.body.appendChild(modalContainer.value);
                }

                // Ensure modal has proper z-index and a new stacking context
                if (modalContainer.value.style.zIndex !== '9999999') {
                    modalContainer.value.style.zIndex = '9999999';
                }
                if (modalContainer.value.style.isolation !== 'isolate') {
                    modalContainer.value.style.isolation = 'isolate';
                }
            });
        }

        // Watch for modal opening to focus on it
        watch(() => props.show, (isOpen) => {
            if (isOpen) {
                // Hoist modal to body for iframe compatibility
                hoistModalToBody();

                // Add modal-open class to body and html
                document.body.classList.add('modal-open');
                document.documentElement.classList.add('modal-open');

                // Prevent body scroll immediately
                document.body.style.overflow = 'hidden';
                document.documentElement.style.overflow = 'hidden';
                document.body.style.position = 'fixed';
                document.body.style.width = '100%';
                document.body.style.top = '0';
                document.body.style.left = '0';
                document.body.style.right = '0';
                document.body.style.margin = '0';
                document.body.style.padding = '0';

                // Also ensure html has no margin/padding
                document.documentElement.style.margin = '0';
                document.documentElement.style.padding = '0';
                document.documentElement.style.width = '100%';
                document.documentElement.style.height = '100%';

                // Notify parent iframe that modal is opening
                if (window.parent && window.parent !== window) {
                    try {
                        window.parent.postMessage({
                            type: 'nsc-scroll-to-top',
                            tabId: window.name || 'event-detail'
                        }, window.location.origin);
                        window.parent.postMessage({
                            type: 'nsc-modal-state',
                            state: 'open'
                        }, window.location.origin);
                    } catch (e) {
                        // Cross-origin, can't communicate
                    }
                }

                nextTick(() => {
                    scrollToTop();

                    // Additional scroll after a short delay to ensure it's at the top
                    setTimeout(() => {
                        scrollToTop();
                    }, 50);

                    setTimeout(() => {
                        scrollToTop();
                    }, 200);
                });
            } else {
                // Remove modal-open class
                document.body.classList.remove('modal-open');
                document.documentElement.classList.remove('modal-open');

                // Restore body scroll when modal closes
                document.body.style.overflow = '';
                document.documentElement.style.overflow = '';
                document.body.style.position = '';
                document.body.style.width = '';
                document.body.style.top = '';
                document.body.style.left = '';
                document.body.style.right = '';
                document.body.style.margin = '';
                document.body.style.padding = '';
                document.documentElement.style.margin = '';
                document.documentElement.style.padding = '';
                document.documentElement.style.width = '';
                document.documentElement.style.height = '';

                // Notify parent iframe that modal is closing
                if (window.parent && window.parent !== window) {
                    try {
                        window.parent.postMessage({
                            type: 'nsc-modal-state',
                            state: 'closed'
                        }, window.location.origin);
                    } catch (e) {
                        // Cross-origin, can't communicate
                    }
                }
            }
        });

        const sortedRooms = computed(() => {
            const rooms = Array.isArray(props.rooms) ? [...props.rooms] : [];
            if (sortBy.value === 'price-low-high') {
                return rooms.sort((a, b) => (a.price_per_night || 0) - (b.price_per_night || 0));
            } else if (sortBy.value === 'price-high-low') {
                return rooms.sort((a, b) => (b.price_per_night || 0) - (a.price_per_night || 0));
            } else if (sortBy.value === 'capacity-low-high') {
                return rooms.sort((a, b) => (a.capacity || 0) - (b.capacity || 0));
            } else if (sortBy.value === 'capacity-high-low') {
                return rooms.sort((a, b) => (b.capacity || 0) - (a.capacity || 0));
            }
            return rooms;
        });

        function handleSelectRoom(room) {
            emit('select-room', room);
        }

        function handleRemoveRoom(roomId) {
            emit('remove-room', roomId);
        }

        function isSelected(roomId) {
            return selectedRoomIds.value.includes(String(roomId));
        }

        function handleContinue() {
            if (safeSelectedRooms.value.length === 0) {
                return;
            }
            emit('continue');
        }

        function changeSlide(roomId, slideIndex) {
            roomSlides.value[roomId] = slideIndex;
            // Reset auto-play timer
            resetAutoPlay(roomId);
        }

        function nextSlide(roomId) {
            const room = props.rooms.find(r => r.id === roomId);
            if (!room || !room.images || room.images.length <= 1) return;

            const currentIndex = getActiveSlide(roomId);
            const nextIndex = (currentIndex + 1) % room.images.length;
            changeSlide(roomId, nextIndex);
        }

        function prevSlide(roomId) {
            const room = props.rooms.find(r => r.id === roomId);
            if (!room || !room.images || room.images.length <= 1) return;

            const currentIndex = getActiveSlide(roomId);
            const prevIndex = currentIndex === 0 ? room.images.length - 1 : currentIndex - 1;
            changeSlide(roomId, prevIndex);
        }

        function startAutoPlay(roomId) {
            const room = props.rooms.find(r => r.id === roomId);
            if (!room || !room.images || room.images.length <= 1) return;

            // Clear existing timer
            if (roomAutoPlayTimers.value[roomId]) {
                clearInterval(roomAutoPlayTimers.value[roomId]);
            }

            // Start new timer (change slide every 4 seconds)
            roomAutoPlayTimers.value[roomId] = setInterval(() => {
                nextSlide(roomId);
            }, 4000);
        }

        function stopAutoPlay(roomId) {
            if (roomAutoPlayTimers.value[roomId]) {
                clearInterval(roomAutoPlayTimers.value[roomId]);
                delete roomAutoPlayTimers.value[roomId];
            }
        }

        function resetAutoPlay(roomId) {
            stopAutoPlay(roomId);
            startAutoPlay(roomId);
        }

        function getActiveSlide(roomId) {
            return roomSlides.value[roomId] || 0;
        }

        // Initialize auto-play for rooms with multiple images
        watch(() => props.rooms, (newRooms) => {
            if (Array.isArray(newRooms)) {
                // Stop all existing timers
                Object.keys(roomAutoPlayTimers.value).forEach(roomId => {
                    stopAutoPlay(roomId);
                });

                // Initialize slides and start auto-play for rooms with multiple images
                newRooms.forEach(room => {
                    if (room.images && room.images.length > 1) {
                        // Initialize slide to 0 if not set
                        if (roomSlides.value[room.id] === undefined) {
                            roomSlides.value[room.id] = 0;
                        }
                        // Start auto-play
                        startAutoPlay(room.id);
                    }
                });
            }
        }, { immediate: true });

        // Cleanup timers on unmount
        onMounted(() => {
            // Hoist modal to body when component is mounted (for iframe compatibility)
            if (props.show) {
                hoistModalToBody();
            }
            try {
                const onResize = () => { isNarrow.value = window.innerWidth < 992; };
                window.addEventListener('resize', onResize);
                // store for cleanup
                modalContainer.__nscOnResize = onResize;
            } catch (e) {
                // ignore
            }
        });

        onUnmounted(() => {
            Object.keys(roomAutoPlayTimers.value).forEach(roomId => {
                stopAutoPlay(roomId);
            });

            // Notify parent iframe that modal is closing on unmount
            if (window.parent && window.parent !== window) {
                try {
                    window.parent.postMessage({
                        type: 'nsc-modal-state',
                        state: 'closed'
                    }, window.location.origin);
                } catch (e) {
                    // Cross-origin, can't communicate
                }
            }

            // cleanup resize
            try {
                if (modalContainer.__nscOnResize) {
                    window.removeEventListener('resize', modalContainer.__nscOnResize);
                }
            } catch (e) {
                // ignore
            }
        });

        function formatPrice(price) {
            if (!price) return '0.00';
            return parseFloat(price).toFixed(2);
        }

        function getRoomTypeDisplay(room) {
            return room.room_type_display || room.room_type || '';
        }

        function getRoomDisplayName(room) {
            // Priority: name > room_type_display > room_type > fallback
            if (room.name && room.name.trim()) {
                return room.name.trim();
            }
            if (room.room_type_display) {
                return room.room_type_display;
            }
            if (room.room_type) {
                return room.room_type;
            }
            return 'Room ' + (room.id || '');
        }

        function getAmenityIconClass(amenity) {
            // amenity can be an object (preferred) or a string
            const iconClassRaw = amenity && typeof amenity === 'object'
                ? (amenity.icon_class || amenity.icon || '')
                : '';

            const normalize = (cls) => String(cls || '')
                .trim()
                // FontAwesome v5 -> v6
                .replace(/\bfas\b/g, 'fa-solid')
                .replace(/\bfar\b/g, 'fa-regular')
                .replace(/\bfab\b/g, 'fa-brands');

            let cls = normalize(iconClassRaw);

            // Normalize some FA5 icon names to FA6 equivalents (common ones used by our backend mapping)
            const fa6NameMap = {
                'fa-swimming-pool': 'fa-person-swimming',
                'fa-glass-martini-alt': 'fa-martini-glass',
                'fa-shuttle-van': 'fa-van-shuttle',
                'fa-play-circle': 'fa-circle-play',
                'fa-check-circle': 'fa-circle-check',
                'fa-tshirt': 'fa-shirt',
            };
            Object.entries(fa6NameMap).forEach(([oldName, newName]) => {
                cls = cls.replace(new RegExp(`\\b${oldName}\\b`, 'g'), newName);
            });

            if (cls) {
                // If backend sent "fa-wifi" only, add prefix for FA6
                if (cls.startsWith('fa-') && !cls.includes('fa-solid') && !cls.includes('fa-regular') && !cls.includes('fa-brands')) {
                    return `fa-solid ${cls} fa-fw`;
                }
                return `${cls} fa-fw`;
            }

            // Fallback icon
            return 'fa-solid fa-star fa-fw';
        }

        // Translation function
        function t(key) {
            return translations[key] || key;
        }

        async function openRoomDetails(room) {
            if (!room || !room.id) return;
            detailError.value = '';
            detailImageIndex.value = 0;

            // Use cached payload if available
            if (detailCache.value[room.id]) {
                detailRoom.value = detailCache.value[room.id];
                // Start autoplay with a small delay
                nextTick(() => {
                    setTimeout(() => startDetailAutoPlay(), 200);
                });
                return;
            }

            detailLoading.value = true;
            detailRoom.value = null;
            try {
                const url = `/locations/ajax/rooms/${room.id}/detail/`;
                const res = await fetch(url, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin',
                });
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                const payload = await res.json();
                detailCache.value[room.id] = payload;
                detailRoom.value = payload;
                detailImageIndex.value = 0;
                // Start autoplay with a small delay
                nextTick(() => {
                    setTimeout(() => startDetailAutoPlay(), 200);
                });
            } catch (e) {
                // Fallback: show at least what we already have on the card
                detailError.value = String(e && e.message ? e.message : e);
                detailRoom.value = {
                    id: room.id,
                    name: room.name || getRoomDisplayName(room),
                    room_type: room.room_type_display || room.room_type || '',
                    description: room.description || '',
                    images: room.images || [],
                    amenities: room.amenities || [],
                    services: [],
                    rules: room.rules || [],
                    capacity: room.capacity,
                    price_per_night: room.price_per_night,
                    price_includes_guests: room.price_includes_guests,
                    additional_guest_price: room.additional_guest_price,
                    breakfast_included: room.breakfast_included,
                };
                detailImageIndex.value = 0;
            } finally {
                detailLoading.value = false;
            }
        }

        function closeRoomDetails() {
            stopDetailAutoPlay();
            detailRoom.value = null;
            detailLoading.value = false;
            detailError.value = '';
            detailImageIndex.value = 0;
        }

        function startDetailAutoPlay() {
            stopDetailAutoPlay();
            if (detailImages.value && detailImages.value.length > 1) {
                detailAutoPlayTimer.value = setInterval(() => {
                    nextDetailImage();
                }, 4000);
            }
        }

        function stopDetailAutoPlay() {
            if (detailAutoPlayTimer.value) {
                clearInterval(detailAutoPlayTimer.value);
                detailAutoPlayTimer.value = null;
            }
        }

        const detailImages = computed(() => {
            const imgs = detailRoom.value && Array.isArray(detailRoom.value.images) ? detailRoom.value.images : [];
            return imgs
                .map((img) => ({
                    url: img && (img.image_url || img.url || ''),
                    alt: img && (img.alt || img.title || '')
                }))
                .filter((x) => !!x.url);
        });

        const activeDetailImage = computed(() => {
            const imgs = detailImages.value;
            if (!imgs.length) return null;
            const idx = Math.min(Math.max(detailImageIndex.value, 0), imgs.length - 1);
            return imgs[idx];
        });

        function setDetailImage(idx) {
            const imgs = detailImages.value;
            if (!imgs.length) return;
            detailImageIndex.value = Math.min(Math.max(idx, 0), imgs.length - 1);
        }

        function nextDetailImage() {
            const imgs = detailImages.value;
            if (!imgs.length) return;
            detailImageIndex.value = (detailImageIndex.value + 1) % imgs.length;
        }

        function prevDetailImage() {
            const imgs = detailImages.value;
            if (!imgs.length) return;
            detailImageIndex.value = detailImageIndex.value === 0 ? imgs.length - 1 : detailImageIndex.value - 1;
        }

        function removeGuest(guestId) {
            // Remove guest from the list
            const updatedGuests = safeGuests.value.filter(g => g.id !== guestId);
            emit('update:guests', updatedGuests);
        }

        function onSelectFromDetail() {
            if (detailRoom.value) {
                console.log('Selecting room from detail overlay:', detailRoom.value.id);
                handleSelectRoom(detailRoom.value);
                // Close the detail overlay so the user sees the main modal updating
                closeRoomDetails();
            }
        }

        return {
            selectedRoomIds,
            safeSelectedRooms,
            sortBy,
            sortedRooms,
            handleSelectRoom,
            handleRemoveRoom,
            onSelectFromDetail,
            isSelected,
            handleContinue,
            changeSlide,
            nextSlide,
            prevSlide,
            startAutoPlay,
            stopAutoPlay,
            getActiveSlide,
            formatPrice,
            getRoomTypeDisplay,
            getRoomDisplayName,
            getAmenityIconClass,
            openRoomDetails,
            closeRoomDetails,
            detailRoom,
            detailLoading,
            detailError,
            detailImages,
            activeDetailImage,
            detailImageIndex,
            setDetailImage,
            nextDetailImage,
            prevDetailImage,
            startDetailAutoPlay,
            stopDetailAutoPlay,
            removeGuest,
            isNarrow,
            showAddGuestModal,
            safeGuests,
            guestsList,
            priceCalculation,
            handleAddGuest,
            handleGuestAdded,
            handleModalScroll,
            modalContainer,
            scrollToTop,
            hoistModalToBody,
            t
        };
    },
    template: `
        <div v-if="show"
             class="modal fade show room-selection-modal-fullscreen"
             style="display: block !important; z-index: 9999999 !important; position: fixed !important; top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important; width: 100vw !important; height: 100vh !important; margin: 0 !important; padding: 20px !important; background: rgba(0, 0, 0, 0.6) !important; backdrop-filter: blur(5px) !important; -webkit-backdrop-filter: blur(5px) !important; overflow: hidden !important; display: flex !important; align-items: center !important; justify-content: center !important; isolation: isolate !important;"
             tabindex="-1"
             @click.self="$emit('close')"
             ref="modalContainer">
            <div class="modal-dialog modal-xl" style="margin: 0 auto !important; max-width: 1400px !important; width: 100% !important; padding: 0 10px !important; display: flex !important; align-items: center !important; justify-content: center !important;">
                <div class="modal-content" style="border-radius: 16px !important; overflow: hidden !important; max-height: 95vh !important; width: 100% !important; max-width: 100% !important; display: flex !important; flex-direction: column !important; margin: 0 !important;">
                    <!-- Enhanced Header -->
                    <div class="modal-header" style="background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); color: white; padding: 12px 16px; border-bottom: none;">
                        <div style="flex: 1;">
                            <h5 class="modal-title" style="font-weight: 800; font-size: 1.1rem; margin: 0; display: flex; align-items: center; gap: 8px; line-height: 1.1;">
                                <i class="fas fa-bed"></i>{{ t('selectRoom') }}
                            </h5>
                            <div v-if="guestsList.length > 0" style="font-size: 0.78rem; margin-top: 3px; opacity: 0.95; line-height: 1.1;">
                                <i class="fas fa-users me-1"></i>{{ guestsList.length }} {{ guestsList.length === 1 ? t('guest') : t('guests') }}
                            </div>
                        </div>
                        <button type="button" class="btn-close btn-close-white" @click="$emit('close')" style="opacity: 0.9; transform: scale(0.9);"></button>
                    </div>

                    <div class="modal-body" style="padding: 24px; overflow: auto; flex: 1 1 auto; min-height: 0; position: relative;">
                        <!-- Room Details Overlay - Clean Modern Design -->
                        <div v-if="detailLoading || detailRoom"
                             style="position: fixed; inset: 0; z-index: 99999; display: flex; flex-direction: column; background: #ffffff; overflow-y: auto; -webkit-overflow-scrolling: touch;">
                            <!-- Simple Header -->
                            <div style="position: sticky; top: 0; z-index: 10; padding: 20px 24px; border-bottom: 1px solid #e5e7eb; background: white; display: flex; align-items: center; justify-content: space-between; gap: 16px;">
                                <button type="button"
                                        @click="closeRoomDetails"
                                        style="width: 36px; height: 36px; border-radius: 50%; border: 1px solid #d1d5db; background: white; color: #374151; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; cursor: pointer; padding: 0;"
                                        onmouseover="this.style.background='#f3f4f6'; this.style.borderColor='#9ca3af';"
                                        onmouseout="this.style.background='white'; this.style.borderColor='#d1d5db';">
                                    <i class="fas fa-times" style="font-size: 0.9rem;"></i>
                                </button>
                            </div>

                            <div style="flex: 1 1 auto;">
                                <div v-if="detailLoading" style="padding: 100px 20px; text-align: center;">
                                    <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: var(--mlb-blue); border-radius: 50%; animation: spin 0.6s linear infinite;"></div>
                                    <div style="margin-top: 20px; color: #6b7280; font-weight: 500;">{{ t('loading') }}</div>
                                </div>
                                <template v-else>
                                    <!-- Image Gallery - Booking.com style -->
                                    <div :style="isNarrow ? 'position: relative; background: #000; margin-bottom: 0;' : 'max-width: 1140px; margin: 0 auto; padding: 24px 24px 0; flex-shrink: 0;'">
                                        <div :style="isNarrow ? 'position: relative; width: 100%; height: 300px; flex-shrink: 0;' : 'position: relative; border-radius: 8px; overflow: hidden; height: 450px; flex-shrink: 0;'">
                                            <img v-if="activeDetailImage"
                                                 :src="activeDetailImage.url"
                                                 :alt="activeDetailImage.alt || (detailRoom && detailRoom.name) || ''"
                                                 style="width: 100%; height: 100%; object-fit: cover; display: block;">
                                            <div v-else :style="isNarrow ? 'height: 300px; display: flex; align-items: center; justify-content: center; background: #f3f4f6;' : 'height: 450px; display: flex; align-items: center; justify-content: center; background: #f3f4f6;'">
                                                <i class="fas fa-image" style="font-size: 3rem; color: #d1d5db;"></i>
                                            </div>

                                            <template v-if="detailImages && detailImages.length > 1">
                                                <button type="button" @click="prevDetailImage(); stopDetailAutoPlay();"
                                                        style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 36px; height: 36px; border-radius: 4px; border: none; background: rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2); cursor: pointer; transition: all 0.2s ease;"
                                                        onmouseover="this.style.background='white';"
                                                        onmouseout="this.style.background='rgba(255,255,255,0.9)';">
                                                    <i class="fas fa-chevron-left" style="color: #262626; font-size: 0.875rem;"></i>
                                                </button>
                                                <button type="button" @click="nextDetailImage(); stopDetailAutoPlay();"
                                                        style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); width: 36px; height: 36px; border-radius: 4px; border: none; background: rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2); cursor: pointer; transition: all 0.2s ease;"
                                                        onmouseover="this.style.background='white';"
                                                        onmouseout="this.style.background='rgba(255,255,255,0.9)';">
                                                    <i class="fas fa-chevron-right" style="color: #262626; font-size: 0.875rem;"></i>
                                                </button>
                                            </template>
                                        </div>

                                        <!-- Thumbnails Strip - Booking.com style -->
                                        <div v-if="detailImages && detailImages.length > 1"
                                             @mouseenter="stopDetailAutoPlay()"
                                             @mouseleave="startDetailAutoPlay()"
                                             :style="isNarrow ? 'display: flex; gap: 6px; padding: 10px 12px; overflow-x: auto; background: #000; scrollbar-width: none; -ms-overflow-style: none;' : 'display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; scrollbar-width: thin;'">
                                            <button v-for="(img, idx) in detailImages" :key="'thumb-'+idx"
                                                    type="button"
                                                    @click="setDetailImage(idx); stopDetailAutoPlay();"
                                                    :style="(idx === detailImageIndex)
                                                        ? (isNarrow
                                                            ? 'flex: 0 0 auto; width: 60px; height: 45px; border-radius: 4px; overflow: hidden; border: 2px solid white; padding: 0; background: transparent; cursor: pointer;'
                                                            : 'flex: 0 0 auto; width: 80px; height: 60px; border-radius: 4px; overflow: hidden; border: 3px solid #0071c2; padding: 0; background: transparent; cursor: pointer;')
                                                        : (isNarrow
                                                            ? 'flex: 0 0 auto; width: 60px; height: 45px; border-radius: 4px; overflow: hidden; border: 2px solid transparent; padding: 0; background: transparent; opacity: 0.6; cursor: pointer;'
                                                            : 'flex: 0 0 auto; width: 80px; height: 60px; border-radius: 4px; overflow: hidden; border: 2px solid #e7e7e7; padding: 0; background: transparent; opacity: 0.7; cursor: pointer;')"
                                                    onmouseover="if (this.style.opacity !== '1') { this.style.opacity='1'; }"
                                                    onmouseout="if (!this.getAttribute('data-active')) { this.style.opacity='0.7'; }">
                                                <img :src="img.url" :alt="img.alt || ''" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Content -->
                                    <div :style="isNarrow ? 'max-width: 100%; padding: 32px 20px 100px;' : 'max-width: 1140px; margin: 0 auto; padding: 48px 24px; display: grid; grid-template-columns: 1.5fr 1fr; gap: 48px;'">
                                        <!-- Main Content -->
                                        <div>
                                            <!-- Title -->
                                            <h1 :style="isNarrow ? 'font-size: 1.5rem; font-weight: 700; color: #003580; margin: 0 0 16px; line-height: 1.3;' : 'font-size: 1.75rem; font-weight: 700; color: #003580; margin: 0 0 16px; line-height: 1.3;'">
                                                {{ detailRoom && detailRoom.name ? detailRoom.name : (detailRoom && detailRoom.room_type ? detailRoom.room_type : '') }}
                                            </h1>

                                            <!-- Quick Info Badges (Booking.com style) -->
                                            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;">
                                                <span v-if="detailRoom && detailRoom.room_type" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: #e7f0ff; border: 1px solid #d6e4ff; border-radius: 4px; font-size: 0.875rem; color: #003580; font-weight: 500;">
                                                    <i class="fas fa-door-open" style="font-size: 0.875rem;"></i>{{ detailRoom.room_type }}
                                                </span>
                                                <span v-if="detailRoom && detailRoom.capacity" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: #e7f0ff; border: 1px solid #d6e4ff; border-radius: 4px; font-size: 0.875rem; color: #003580; font-weight: 500;">
                                                    <i class="fas fa-users" style="font-size: 0.875rem;"></i>{{ detailRoom.capacity }} {{ t('people') }}
                                                </span>
                                                <span v-if="detailRoom && detailRoom.breakfast_included" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: #e7f0ff; border: 1px solid #d6e4ff; border-radius: 4px; font-size: 0.875rem; color: #003580; font-weight: 500;">
                                                    <i class="fas fa-coffee" style="font-size: 0.875rem;"></i>{{ t('breakfast') }}
                                                </span>
                                                <span v-if="detailRoom && detailRoom.room_number" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: #e7f0ff; border: 1px solid #d6e4ff; border-radius: 4px; font-size: 0.875rem; color: #003580; font-weight: 500;">
                                                    <i class="fas fa-hashtag" style="font-size: 0.875rem;"></i>{{ detailRoom.room_number }}
                                                </span>
                                            </div>

                                            <!-- Description -->
                                            <div v-if="detailRoom && detailRoom.description" style="margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #e7e7e7;">
                                                <p style="color: #262626; line-height: 1.6; font-size: 0.9375rem; margin: 0; white-space: pre-wrap;">{{ detailRoom.description }}</p>
                                            </div>

                                            <!-- Amenities -->
                                            <div v-if="detailRoom && detailRoom.amenities && detailRoom.amenities.length" style="margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #e7e7e7;">
                                                <h3 style="font-size: 1.125rem; font-weight: 700; color: #262626; margin: 0 0 16px;">{{ t('amenities') }}</h3>
                                                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px;">
                                                    <div v-for="(a, idx) in detailRoom.amenities" :key="'amenity-'+idx" style="display: flex; align-items: flex-start; gap: 10px;">
                                                        <i class="fas fa-check" style="font-size: 0.875rem; color: #008009; margin-top: 2px; flex-shrink: 0;"></i>
                                                        <span style="color: #262626; font-size: 0.9375rem; line-height: 1.5;">{{ a.name || a }}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Services (if available) -->
                                            <div v-if="detailRoom && detailRoom.services && detailRoom.services.length" style="margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #e7e7e7;">
                                                <h3 style="font-size: 1.125rem; font-weight: 700; color: #262626; margin: 0 0 16px;">{{ t('services') }}</h3>
                                                <div style="display: grid; gap: 12px;">
                                                    <div v-for="(s, idx) in detailRoom.services" :key="'service-'+idx" style="display: flex; align-items: flex-start; gap: 10px;">
                                                        <i class="fas fa-check" style="font-size: 0.875rem; color: #008009; margin-top: 2px; flex-shrink: 0;"></i>
                                                        <div style="flex: 1;">
                                                            <div style="display: flex; justify-content: space-between; align-items: start; gap: 12px;">
                                                                <span style="color: #262626; font-size: 0.9375rem; font-weight: 500;">{{ s.name || s.service_name }}</span>
                                                                <span v-if="s.price" style="color: #262626; font-size: 0.9375rem; font-weight: 600; white-space: nowrap;">
                                                                    \${{ s.price }}<template v-if="s.is_per_person || s.is_per_night"><span style="font-weight: 400; color: #6b6b6b;">/<template v-if="s.is_per_person">{{ t('person') }}</template><template v-if="s.is_per_night">{{ t('night') }}</template></span></template>
                                                                </span>
                                                            </div>
                                                            <p v-if="s.description" style="color: #6b6b6b; font-size: 0.875rem; margin: 4px 0 0; line-height: 1.5;">{{ s.description }}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Rules (if available) -->
                                            <div v-if="detailRoom && detailRoom.rules && detailRoom.rules.length" style="margin-bottom: 32px;">
                                                <h3 style="font-size: 1.125rem; font-weight: 700; color: #262626; margin: 0 0 16px;">{{ t('rules') }}</h3>
                                                <div style="display: grid; gap: 12px;">
                                                    <div v-for="(r, idx) in detailRoom.rules" :key="'rule-'+idx" style="display: flex; align-items: flex-start; gap: 10px;">
                                                        <i class="fas fa-info-circle" style="font-size: 0.875rem; color: #0071c2; margin-top: 2px; flex-shrink: 0;"></i>
                                                        <div>
                                                            <span style="color: #262626; font-size: 0.9375rem; line-height: 1.5;">{{ r.description || (t('rule') + ' ' + (idx + 1)) }}</span>
                                                            <div v-if="r.min_adults != null || r.min_children != null" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px;">
                                                                <span v-if="r.min_adults != null" style="padding: 3px 8px; background: #f5f5f5; border-radius: 4px; font-size: 0.8125rem; color: #6b6b6b;">
                                                                    {{ t('adults') }}: {{ r.min_adults }}{{ r.max_adults ? ' - ' + r.max_adults : '+' }}
                                                                </span>
                                                                <span v-if="r.min_children != null" style="padding: 3px 8px; background: #f5f5f5; border-radius: 4px; font-size: 0.8125rem; color: #6b6b6b;">
                                                                    {{ t('children') }}: {{ r.min_children }}{{ r.max_children ? ' - ' + r.max_children : '+' }}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Sidebar - Price Card (Booking.com style) -->
                                        <div :style="isNarrow ? 'position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid #e7e7e7; padding: 16px 20px; z-index: 10; box-shadow: 0 -2px 8px rgba(0,0,0,0.1);' : 'position: sticky; top: 100px; height: fit-content;'">
                                            <div :style="isNarrow ? '' : 'border: 1px solid #e7e7e7; border-radius: 4px; padding: 24px; background: #febb02; background: linear-gradient(180deg, #fff9e6 0%, #ffffff 100%);'">
                                                <div :style="isNarrow ? 'display: flex; justify-content: space-between; align-items: center; gap: 16px;' : ''">
                                                    <div :style="isNarrow ? '' : 'margin-bottom: 20px;'">
                                                        <div :style="isNarrow ? 'font-size: 1.5rem; font-weight: 700; color: #262626; line-height: 1;' : 'font-size: 2rem; font-weight: 700; color: #262626; line-height: 1; margin-bottom: 4px;'">
                                                            \${{ formatPrice(detailRoom && detailRoom.price_per_night) }}
                                                        </div>
                                                        <div :style="isNarrow ? 'font-size: 0.75rem; color: #6b6b6b; margin-top: 2px;' : 'font-size: 0.875rem; color: #6b6b6b; margin-top: 4px;'">
                                                            {{ t('per') }} {{ t('night') }}
                                                        </div>
                                                        <div v-if="detailRoom && detailRoom.price_includes_guests" style="margin-top: 12px; padding: 10px; background: white; border-radius: 4px; font-size: 0.875rem; color: #262626;">
                                                            <i class="fas fa-check" style="color: #008009; margin-right: 6px;"></i>
                                                            {{ t('priceIncludes') }} {{ detailRoom.price_includes_guests }} {{ detailRoom.price_includes_guests === 1 ? t('guest') : t('guests') }}
                                                        </div>
                                                        <div v-if="detailRoom && detailRoom.additional_guest_price && detailRoom.additional_guest_price > 0" style="margin-top: 8px; font-size: 0.8125rem; color: #6b6b6b;">
                                                            + \${{ formatPrice(detailRoom.additional_guest_price) }} {{ t('per') }} {{ t('additionalGuest') }}
                                                        </div>
                                                    </div>
                                                    <!-- Select Room Button -->
                                                    <button type="button"
                                                            @click="onSelectFromDetail"
                                                            :style="{
                                                                width: isNarrow ? 'auto' : '100%',
                                                                padding: isNarrow ? '12px 20px' : '16px 24px',
                                                                borderRadius: '4px',
                                                                border: 'none',
                                                                color: 'white',
                                                                fontWeight: '600',
                                                                fontSize: isNarrow ? '0.9375rem' : '1rem',
                                                                cursor: 'pointer',
                                                                transition: 'all 0.2s ease',
                                                                whiteSpace: 'nowrap',
                                                                background: (detailRoom && isSelected(detailRoom.id)) ? '#d32f2f' : '#0071c2'
                                                            }"
                                                            onmouseover="this.style.opacity='0.9';"
                                                            onmouseout="this.style.opacity='1';">
                                                        <template v-if="detailRoom && isSelected(detailRoom.id)">
                                                            <i class="fas fa-times-circle me-2"></i>{{ t('remove') }}
                                                        </template>
                                                        <template v-else>
                                                            {{ t('selectRoom') }}
                                                        </template>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Error -->
                                    <div v-if="detailError" :style="isNarrow ? 'padding: 0 20px 80px;' : 'max-width: 1140px; margin: 0 auto; padding: 0 24px 48px;'">
                                        <div style="padding: 12px 16px; border-radius: 8px; background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; font-size: 0.875rem; display: flex; align-items: center; gap: 8px;">
                                            <i class="fas fa-exclamation-circle"></i>
                                            <span>{{ detailError }}</span>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <!-- Compact Guests & Price Summary -->
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 20px;">
                            <!-- Guests Summary -->
                            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border: 2px solid #e9ecef; border-radius: 12px; padding: 16px;">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                    <div style="font-weight: 700; color: var(--mlb-blue); font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                                        <i class="fas fa-users"></i>{{ t('yourGuests') }}
                                        <span style="background: var(--mlb-blue); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                            {{ guestsList.length }}
                                        </span>
                                    </div>
                                    <button type="button"
                                            class="btn btn-sm"
                                            @click="handleAddGuest"
                                            style="background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); color: white; border: none; border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; font-weight: 600;">
                                        <i class="fas fa-plus me-1"></i>{{ t('addGuest') }}
                                    </button>
                                </div>
                                <div style="display: flex; gap: 8px; overflow-x: auto; overflow-y: hidden; white-space: nowrap; padding-bottom: 6px;">
                                    <div v-for="guest in guestsList" :key="guest.id"
                                         style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; background: white; border-radius: 8px; border: 1px solid #e9ecef; font-size: 0.8rem; flex: 0 0 auto;">
                                        <span style="font-weight: 600; color: var(--mlb-blue);">{{ guest.displayName }}</span>
                                        <span v-if="guest.isRegistrant"
                                              style="font-size: 0.65rem; padding: 2px 5px; background: var(--mlb-red); color: white; border-radius: 4px; font-weight: 700;">
                                            {{ t('registrant') }}
                                        </span>
                                        <span v-else-if="guest.isPlayer"
                                              style="font-size: 0.65rem; padding: 2px 5px; background: var(--mlb-blue); color: white; border-radius: 4px; font-weight: 700;">
                                            {{ t('player') }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- Price Summary -->
                            <div style="background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%); border: 2px solid #fecaca; border-radius: 12px; padding: 16px;">
                                <div style="font-weight: 700; color: var(--mlb-red); font-size: 0.95rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                                    <i class="fas fa-calculator"></i>{{ t('priceCalculation') }}
                                </div>
                                <div v-if="safeSelectedRooms.length === 0" style="color: #6c757d; font-style: italic; font-size: 0.85rem; text-align: center; padding: 20px 0;">
                                    {{ t('selectRoomToSeePrice') }}
                                </div>
                                <div v-else style="font-size: 0.9rem;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; color: #64748b;">
                                        <span>{{ t('basePrice') }}:</span>
                                        <strong style="color: #333;">\${{ formatPrice(priceCalculation.basePrice) }}</strong>
                                    </div>
                                    <div v-if="priceCalculation.additionalGuests > 0" style="display: flex; justify-content: space-between; margin-bottom: 8px; color: #64748b; font-size: 0.85rem;">
                                        <span>{{ t('additionalGuests') }}:</span>
                                        <span>\${{ formatPrice(priceCalculation.additionalGuests) }}</span>
                                    </div>
                                    <hr style="margin: 10px 0; border-top: 2px solid #fecaca;">
                                    <div style="display: flex; justify-content: space-between; font-weight: 800; color: var(--mlb-red); font-size: 1.1rem;">
                                        <span>{{ t('total') }}:</span>
                                        <span>\${{ formatPrice(priceCalculation.total) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Rooms Section Header with Sort -->
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; padding: 12px 16px; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-bed" style="color: var(--mlb-blue); font-size: 1.1rem;"></i>
                                <span style="font-weight: 700; color: #333; font-size: 1rem;">{{ t('availableRooms') }}</span>
                                <span v-if="sortedRooms.length > 0" style="background: var(--mlb-blue); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                    {{ sortedRooms.length }}
                                </span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-sort" style="color: var(--mlb-blue); font-size: 0.9rem;"></i>
                                <select v-model="sortBy"
                                        style="padding: 8px 12px; border: 2px solid #ced4da; border-radius: 8px; font-size: 0.85rem; background: white; color: #333; cursor: pointer; min-width: 200px; font-weight: 600; transition: all 0.3s ease;"
                                        @change="sortBy = $event.target.value">
                                    <option value="recommended">{{ t('recommended') }}</option>
                                    <option value="price-low-high">{{ t('priceLowToHigh') }}</option>
                                    <option value="price-high-low">{{ t('priceHighToLow') }}</option>
                                    <option value="capacity-low-high">{{ t('capacityLowToHigh') }}</option>
                                    <option value="capacity-high-low">{{ t('capacityHighToLow') }}</option>
                                </select>
                            </div>
                        </div>

                        <!-- Rooms Grid -->
                        <div class="rooms-grid-container" style="padding: 8px; background: #f8f9fa; border-radius: 12px;">
                            <div v-for="room in sortedRooms" :key="room.id"
                                 class="room-listing-inline"
                                 :data-selected="isSelected(room.id)"
                                 @click="handleSelectRoom(room)">
                                <!-- Room Image Slider -->
                                <div class="room-image-container"
                                     @mouseenter="stopAutoPlay(room.id)"
                                     @mouseleave="startAutoPlay(room.id)">
                                    <div class="room-slider-wrapper">
                                        <template v-if="room.images && room.images.length > 0">
                                            <div v-for="(image, index) in room.images"
                                                 :key="'room-' + room.id + '-img-' + index"
                                                 class="room-slide"
                                                 :class="{ active: getActiveSlide(room.id) === index }">
                                                <img :src="image.url" :alt="image.alt || room.name" loading="lazy">
                                            </div>
                                        </template>
                                        <template v-else>
                                            <div class="room-slide active">
                                                <div style="background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); display: flex; align-items: center; justify-content: center; width: 100%; height: 100%;">
                                                    <i class="fas fa-bed" style="color: white; font-size: 1.5rem;"></i>
                                                </div>
                                            </div>
                                        </template>
                                    </div>

                                    <!-- Navigation Arrows -->
                                    <template v-if="room.images && room.images.length > 1">
                                        <button type="button"
                                                class="room-slider-nav prev"
                                                @click.stop="prevSlide(room.id)"
                                                aria-label="Previous image">
                                            <i class="fas fa-chevron-left"></i>
                                        </button>
                                        <button type="button"
                                                class="room-slider-nav next"
                                                @click.stop="nextSlide(room.id)"
                                                aria-label="Next image">
                                            <i class="fas fa-chevron-right"></i>
                                        </button>

                                        <!-- Dots Navigation -->
                                        <div class="room-slider-dots">
                                            <span v-for="(image, index) in room.images"
                                                  :key="'dot-' + room.id + '-' + index"
                                                  class="room-dot"
                                                  :class="{ active: getActiveSlide(room.id) === index }"
                                                  @click.stop="changeSlide(room.id, index)"
                                                  :aria-label="'Go to image ' + (index + 1)"></span>
                                        </div>
                                    </template>
                                </div>

                                <!-- Room Info -->
                                <div class="room-info">
                                    <div class="room-header">
                                        <div class="room-title-row" style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                                            <div class="room-name" style="flex: 1; min-width: 0;">{{ getRoomDisplayName(room) }}</div>
                                            <span v-if="room.breakfast_included"
                                                  class="room-badge-breakfast"
                                                  style="flex: 0 0 auto; display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 800; color: #065f46; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 1px solid #86efac; box-shadow: 0 1px 2px rgba(5, 150, 105, 0.12); white-space: nowrap;">
                                                <i class="fas fa-coffee" style="font-size: 0.75rem;"></i>
                                                {{ t('breakfast') }}
                                            </span>
                                        </div>
                                        <div v-if="getRoomTypeDisplay(room) && room.name" class="room-type">{{ getRoomTypeDisplay(room) }}</div>
                                        <!-- room number hidden (requested) -->
                                    </div>

                                    <div class="room-content-wrapper">
                                        <div class="room-meta-row">
                                            <div class="room-features">
                                                <span v-if="room.capacity">
                                                    <i class="fas fa-users" style="font-size: 0.7rem;"></i>
                                                    <strong>{{ t('max') }} {{ room.capacity }}</strong> {{ t('people') }}
                                                </span>
                                                <!-- breakfast badge moved to header (requested) -->
                                                <!-- room number hidden (requested) -->
                                            </div>

                                            <div v-if="room.amenities && room.amenities.length > 0" class="room-amenities">
                                                <span v-for="(amenity, index) in room.amenities.slice(0, 6)"
                                                      :key="index"
                                                      :title="amenity.name || amenity">
                                                    <i :class="getAmenityIconClass(amenity)" style="font-size: 0.85rem;"></i>
                                                </span>
                                                <span v-if="room.amenities.length > 6" style="font-size: 0.7rem; color: #64748b; align-self: center; font-weight: 700; padding: 4px 8px; background: #f1f5f9; border-radius: 6px; border: 1px solid #e2e8f0;">
                                                    +{{ room.amenities.length - 6 }}
                                                </span>
                                            </div>
                                        </div>

                                        <div class="room-footer">
                                            <div class="room-price-zone">
                                                <div class="room-price-wrapper">
                                                    <div class="room-price">
                                                        \${{ formatPrice(room.price_per_night) }}
                                                        <small>/ {{ t('night') }}</small>
                                                    </div>
                                                    <div v-if="room.price_includes_guests" class="room-price-includes" :title="t('basePriceIncludes')">
                                                        <i class="fas fa-users"></i>
                                                        <span>{{ t('priceIncludes') }} <strong>{{ room.price_includes_guests }}</strong> {{ room.price_includes_guests === 1 ? t('guest') : t('guests') }}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="room-actions">
                                                <button type="button"
                                                        class="btn btn-sm btn-outline-primary room-detail-btn"
                                                        @click.stop="openRoomDetails(room)"
                                                        style="border-radius: 10px; font-weight: 700; padding: 9px 18px; border-width: 2px; font-size: 0.85rem; white-space: nowrap; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border-color: var(--mlb-blue); color: var(--mlb-blue); background: transparent; box-shadow: 0 2px 4px rgba(13, 44, 84, 0.1); width: 100%;">
                                                    <i class="fas fa-eye me-1"></i>{{ t('details') }}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer" style="background: #f8f9fa; border-top: 1px solid #e9ecef; padding: 6px 10px; margin: 0; min-height: unset; display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;">
                        <div class="me-auto" style="display: flex; align-items: center; gap: 8px; margin: 0;">
                            <div v-if="safeSelectedRooms.length > 0" style="display: flex; align-items: center; gap: 6px; padding: 6px 10px; background: white; border-radius: 8px; border: 1px solid rgba(13, 44, 84, 0.35);">
                                <i class="fas fa-check-circle" style="color: var(--mlb-blue);"></i>
                                <span style="font-weight: 700; color: var(--mlb-blue); font-size: 0.85rem; line-height: 1.1;">
                                    {{ safeSelectedRooms.length }} {{ safeSelectedRooms.length === 1 ? t('room') : t('rooms') }} {{ t('selected') }}
                                </span>
                            </div>
                            <div v-else style="color: #6c757d; font-size: 0.8rem; font-style: italic; line-height: 1.1;">
                                <i class="fas fa-info-circle me-1"></i>{{ t('selectRoomToContinue') }}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; margin-left: auto; align-items: center;">
                            <button type="button"
                                    class="btn btn-secondary"
                                    @click="$emit('close')"
                                    style="padding: 8px 14px; font-weight: 600; border-radius: 8px; line-height: 1.1;">
                                {{ t('cancel') }}
                            </button>
                            <button
                                type="button"
                                class="btn btn-primary"
                                @click="handleContinue"
                                :disabled="safeSelectedRooms.length === 0"
                                style="padding: 8px 16px; font-weight: 700; border-radius: 8px; background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); border: none; box-shadow: 0 3px 10px rgba(13, 44, 84, 0.25); transition: all 0.3s ease; line-height: 1.1;"
                                :style="safeSelectedRooms.length === 0 ? 'opacity: 0.5; cursor: not-allowed;' : 'opacity: 1;'">
                                <i class="fas fa-arrow-right me-2"></i>{{ t('continue') }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="show" class="modal-backdrop fade show" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9998; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(4px);"></div>

        <!-- Add Guest Modal -->
        <AddGuestModal
            :show="showAddGuestModal"
            :hotel-pk="hotelPk"
            @close="showAddGuestModal = false"
            @guest-added="handleGuestAdded" />
    `
};

/**
 * Add Guest Modal Component
 */
const AddGuestModal = {
    props: {
        show: Boolean,
        hotelPk: String
    },
    emits: ['close', 'guest-added'],
    setup(props, { emit }) {
        const formData = ref({
            first_name: '',
            last_name: '',
            email: '',
            birth_date: '',
            guest_type: 'adult'
        });

        const maxDate = computed(() => {
            const today = new Date();
            return today.toISOString().split('T')[0];
        });

        function calculateAge(birthDate) {
            if (!birthDate) return null;
            const today = new Date();
            const birth = new Date(birthDate);
            let age = today.getFullYear() - birth.getFullYear();
            const monthDiff = today.getMonth() - birth.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
                age--;
            }
            return age;
        }

        function handleBirthDateChange() {
            if (formData.value.birth_date) {
                const age = calculateAge(formData.value.birth_date);
                if (age !== null) {
                    formData.value.guest_type = age >= 18 ? 'adult' : 'child';
                }
            }
        }

        function handleSubmit() {
            if (!formData.value.first_name || !formData.value.last_name || !formData.value.email || !formData.value.birth_date) {
                return;
            }

            const guest = {
                ...formData.value,
                id: `guest-${Date.now()}`,
                age: calculateAge(formData.value.birth_date),
                type: formData.value.guest_type
            };

            emit('guest-added', guest);
            resetForm();
        }

        function resetForm() {
            formData.value = {
                first_name: '',
                last_name: '',
                email: '',
                birth_date: '',
                guest_type: 'adult'
            };
        }

        function handleClose() {
            resetForm();
            emit('close');
        }

        // Translation function
        function t(key) {
            return translations[key] || key;
        }

        return {
            formData,
            maxDate,
            handleBirthDateChange,
            handleSubmit,
            handleClose,
            t
        };
    },
    template: `
        <div v-if="show" class="modal fade show" style="display: block; z-index: 1060;" tabindex="-1" @click.self="handleClose">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius: 16px; overflow: hidden; border: none; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                    <div class="modal-header" style="background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); color: white; padding: 16px 20px;">
                        <h5 class="modal-title">
                            <i class="fas fa-user-plus me-2"></i>{{ t('addGuest') }}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" @click="handleClose"></button>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
                        <form @submit.prevent="handleSubmit">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">
                                        <i class="fas fa-user me-1"></i>{{ t('firstName') }} <span class="text-danger">*</span>
                                    </label>
                                    <input type="text"
                                           class="form-control"
                                           v-model="formData.first_name"
                                           required
                                           :placeholder="t('enterFirstName')">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">
                                        <i class="fas fa-user me-1"></i>{{ t('lastName') }} <span class="text-danger">*</span>
                                    </label>
                                    <input type="text"
                                           class="form-control"
                                           v-model="formData.last_name"
                                           required
                                           :placeholder="t('enterLastName')">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">
                                        <i class="fas fa-envelope me-1"></i>{{ t('email') }} <span class="text-danger">*</span>
                                    </label>
                                    <input type="email"
                                           class="form-control"
                                           v-model="formData.email"
                                           required
                                           :placeholder="t('enterEmailAddress')">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">
                                        <i class="fas fa-calendar me-1"></i>{{ t('dateOfBirth') }} <span class="text-danger">*</span>
                                    </label>
                                    <input type="date"
                                           class="form-control"
                                           v-model="formData.birth_date"
                                           :max="maxDate"
                                           @change="handleBirthDateChange"
                                           required>
                                </div>
                                <div class="col-md-12">
                                    <label class="form-label">
                                        <i class="fas fa-users me-1"></i>{{ t('guestType') }} <span class="text-danger">*</span>
                                    </label>
                                    <div class="d-flex gap-3">
                                        <div class="form-check">
                                            <input class="form-check-input"
                                                   type="radio"
                                                   v-model="formData.guest_type"
                                                   id="guestTypeAdult"
                                                   value="adult">
                                            <label class="form-check-label" for="guestTypeAdult">
                                                <i class="fas fa-user me-1"></i>{{ t('adult') }} (18+)
                                            </label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input"
                                                   type="radio"
                                                   v-model="formData.guest_type"
                                                   id="guestTypeChild"
                                                   value="child">
                                            <label class="form-check-label" for="guestTypeChild">
                                                <i class="fas fa-child me-1"></i>{{ t('child') }} (<18)
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid #e9ecef; padding: 16px 20px; background: #ffffff;">
                        <button type="button" class="btn btn-form-cancel" @click="handleClose" style="padding: 12px 22px;">
                            {{ t('cancel') }}
                        </button>
                        <button type="button" class="btn btn-form-submit" @click="handleSubmit" style="padding: 12px 22px;">
                            <i class="fas fa-save me-2"></i>{{ t('saveGuest') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="show" class="modal-backdrop fade show" style="z-index: 1055;"></div>
    `
};

/**
 * Guest Details Modal Component
 */
const GuestDetailsModal = {
    props: {
        hotelPk: String,
        guests: Array,
        show: Boolean
    },
    emits: ['close', 'add-guest', 'remove-guest', 'continue'],
    setup(props, { emit }) {
        const adults = ref([]);
        const children = ref([]);

        function addAdult() {
            adults.value.push({
                name: '',
                email: '',
                phone: '',
                birthdate: ''
            });
        }

        function removeAdult(index) {
            adults.value.splice(index, 1);
        }

        function addChild() {
            children.value.push({
                name: '',
                birthdate: ''
            });
        }

        function removeChild(index) {
            children.value.splice(index, 1);
        }

        function handleContinue() {
            const allGuests = [
                ...adults.value.map(a => ({ ...a, type: 'adult' })),
                ...children.value.map(c => ({ ...c, type: 'child' }))
            ];
            emit('continue', allGuests);
        }

        // Translation function
        function t(key) {
            return translations[key] || key;
        }

        return {
            adults,
            children,
            addAdult,
            removeAdult,
            addChild,
            removeChild,
            handleContinue,
            t
        };
    },
    template: `
        <div v-if="show" class="modal fade show" style="display: block;" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Guest Details</h5>
                        <button type="button" class="btn-close" @click="$emit('close')"></button>
                    </div>
                    <div class="modal-body">
                        <h6>Adults</h6>
                        <div v-for="(adult, index) in adults" :key="index" class="mb-3">
                            <div class="row g-2">
                                <div class="col-md-6">
                                    <input v-model="adult.name" type="text" class="form-control" placeholder="Name" required>
                                </div>
                                <div class="col-md-6">
                                    <input v-model="adult.email" type="email" class="form-control" placeholder="Email" required>
                                </div>
                                <div class="col-md-6">
                                    <input v-model="adult.phone" type="tel" class="form-control" placeholder="Phone" required>
                                </div>
                                <div class="col-md-4">
                                    <input v-model="adult.birthdate" type="date" class="form-control" required>
                                </div>
                                <div class="col-md-2">
                                    <button @click="removeAdult(index)" class="btn btn-danger btn-sm">Remove</button>
                                </div>
                            </div>
                        </div>
                        <button @click="addAdult" class="btn btn-outline-primary btn-sm mb-3">Add Adult</button>

                        <h6>Children</h6>
                        <div v-for="(child, index) in children" :key="index" class="mb-3">
                            <div class="row g-2">
                                <div class="col-md-6">
                                    <input v-model="child.name" type="text" class="form-control" placeholder="Name" required>
                                </div>
                                <div class="col-md-4">
                                    <input v-model="child.birthdate" type="date" class="form-control" required>
                                </div>
                                <div class="col-md-2">
                                    <button @click="removeChild(index)" class="btn btn-danger btn-sm">Remove</button>
                                </div>
                            </div>
                        </div>
                        <button @click="addChild" class="btn btn-outline-primary btn-sm">Add Child</button>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="handleContinue">Continue</button>
                    </div>
                </div>
            </div>
        </div>
    `
};

/**
 * Toast Component
 */
const ToastComponent = {
    props: {
        toasts: {
            type: Array,
            default: () => []
        }
    },
    setup(props) {
        const hasToasts = computed(() => {
            return Array.isArray(props.toasts) && props.toasts.length > 0;
        });
        return {
            hasToasts
        };
    },
    template: `
        <div v-if="hasToasts" class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 3000001;">
            <div
                v-for="toast in toasts"
                :key="toast.id"
                class="toast show"
                :class="'bg-' + toast.type">
                <div class="toast-body text-white">
                    {{ toast.message }}
                </div>
            </div>
        </div>
    `
};

// ============================================
// Main Event Detail Component
// ============================================

const RoomSelectionModalWithComponents = {
    components: {
        AddGuestModal
    },
    ...RoomSelectionModal
};

const EventDetailApp = {
    components: {
        RoomSelectionModal: RoomSelectionModalWithComponents,
        GuestDetailsModal,
        ToastComponent,
        AddGuestModal
    },
    setup() {
        // Get hotel PK and event PK from the mounted element's data attribute
        // Find the element that will be mounted (by pattern)
        let initialPk = '';
        let eventPk = '';
        const appEl = document.querySelector('[id^="event-detail-app"]');
        if (appEl) {
            initialPk = appEl.dataset.hotelPk || '';
            eventPk = appEl.dataset.eventPk || '';
        }

        const hotelPk = ref(initialPk);
        const eventPkRef = ref(eventPk);

        // Event data
        const eventData = ref(null);
        const children = ref([]);
        const selectedChildren = ref([]);
        const registrant = ref(null);

        // Initialize services
        const reservation = useHotelReservation(hotelPk.value);
        const priceCalc = usePriceCalculation(hotelPk.value, reservation.state);
        const toast = useToast();

        // UI State
        const showRoomModal = ref(false);
        const showGuestModal = ref(false);
        const rooms = ref([]);
        const loading = ref(false);

        // Load rooms from server
        async function loadRooms() {
            if (!hotelPk.value) return;

            loading.value = true;
            try {
                // Get rooms data from template using hotel PK
                const roomsDataEl = document.getElementById(`rooms-data-${hotelPk.value}`);
                if (roomsDataEl) {
                    rooms.value = JSON.parse(roomsDataEl.textContent);
                } else {
                    // Fallback to generic ID
                    const fallbackEl = document.getElementById('rooms-data');
                    if (fallbackEl) {
                        rooms.value = JSON.parse(fallbackEl.textContent);
                    }
                }
            } catch (error) {
                console.error('Error loading rooms:', error);
                toast.show('Error loading rooms', 'error');
            } finally {
                loading.value = false;
            }
        }

        function handleSelectRoom(room) {
            if (!room || !room.id) {
                console.error('Invalid room object for selection:', room);
                return;
            }

            const roomIdStr = String(room.id);
            console.log('Parent handleSelectRoom called for room:', roomIdStr);
            const existing = reservation.state.rooms.find(r => r.roomId === roomIdStr);

            // If already selected -> toggle off
            if (existing) {
                console.log('Toggling OFF room:', roomIdStr);
                reservation.removeRoom(roomIdStr);
                toast.show(`Room "${existing.roomLabel || room.name || roomIdStr}" removed`, 'info');
            } else {
                console.log('Toggling ON room:', roomIdStr);
                const label = (room.name && String(room.name).trim())
                    ? String(room.name).trim()
                    : (room.room_type_display || room.room_type || `Room ${roomIdStr}`);

                reservation.addRoom(
                    roomIdStr,
                    label,
                    room.capacity,
                    room.price_per_night || room.price || 0,
                    room.price_includes_guests || 1,
                    room.additional_guest_price || 0
                );
                toast.show(`Room "${label}" added`, 'success');
            }

            console.log('Total rooms selected now:', reservation.state.rooms.length);

            // If guests already exist, keep assignments consistent
            if (Array.isArray(reservation.state.guests) && reservation.state.guests.length > 0) {
                reservation.autoDistributeGuests();
            }
        }

        function handleRemoveRoom(roomId) {
            const room = reservation.state.rooms.find(r => r.roomId === String(roomId));
            if (room) {
                reservation.removeRoom(roomId);
                toast.show(`Room "${room.roomLabel}" removed`, 'info');
            }

            if (Array.isArray(reservation.state.guests) && reservation.state.guests.length > 0) {
                reservation.autoDistributeGuests();
            }
        }

        function handleAddGuest(guest) {
            if (!reservation.state.guests) {
                reservation.state.guests = [];
            }
            reservation.state.guests.push(guest);
            toast.show(`Guest "${guest.first_name} ${guest.last_name}" added`, 'success');
        }

        function handleGuestDetailsContinue(allGuests) {
            reservation.state.guests = allGuests;
            reservation.autoDistributeGuests();
            showGuestModal.value = false;
            toast.show('Guests added successfully', 'success');
        }

        function handleContinueToCheckout() {
            // Validate and proceed to checkout
            if (reservation.state.rooms.length === 0) {
                toast.show('Please select at least one room', 'warning');
                return;
            }
            if (reservation.state.guests.length === 0) {
                toast.show('Please add guest details', 'warning');
                return;
            }

            // Submit form or redirect to checkout
            const form = document.getElementById('hotel-reservation-form');
            if (form) {
                // Update hidden inputs
                const roomInput = document.getElementById(`guest-room${hotelPk.value}`);
                if (roomInput && reservation.state.rooms.length > 0) {
                    roomInput.value = reservation.state.rooms[0].roomId;
                }
                form.submit();
            }
        }

        // Load event data
        function loadEventData() {
            const eventDataEl = document.getElementById('event-data');
            if (eventDataEl) {
                try {
                    eventData.value = JSON.parse(eventDataEl.textContent);
                } catch (e) {
                    console.error('Error loading event data:', e);
                }
            }
        }

        // Load registrant data
        function loadRegistrantData() {
            const registrantDataEl = document.getElementById('registrant-data');
            if (registrantDataEl) {
                try {
                    registrant.value = JSON.parse(registrantDataEl.textContent);
                } catch (e) {
                    console.error('Error loading registrant data:', e);
                }
            }
        }

        // Load children data
        function loadChildrenData() {
            const childrenDataEl = document.getElementById('children-data');
            if (childrenDataEl) {
                try {
                    children.value = JSON.parse(childrenDataEl.textContent);
                } catch (e) {
                    console.error('Error loading children data:', e);
                }
            }
        }

        // Toggle child selection
        function toggleChild(childId) {
            const child = children.value.find(c => c.id === childId);
            if (child && child.registered) {
                return; // Don't allow selection of registered children
            }
            const index = selectedChildren.value.indexOf(childId);
            if (index === -1) {
                selectedChildren.value.push(childId);
            } else {
                selectedChildren.value.splice(index, 1);
            }
            updateCheckoutSummary();
        }

        // Translation function for templates
        function $t(key) {
            return translations[key] || key;
        }

        // Helper functions
        function formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        }

        function formatPrice(amount) {
            return `$${parseFloat(amount || 0).toFixed(2)}`;
        }

        function formatLocation(event) {
            if (!event) return '';
            const parts = [];
            if (event.city) parts.push(event.city.name);
            if (event.state) parts.push(event.state.name);
            if (event.country) parts.push(event.country.name);
            if (parts.length === 0 && event.location) return event.location;
            return parts.join(', ');
        }

        function getInitials(name) {
            if (!name) return '';
            const parts = name.split(' ');
            if (parts.length >= 2) {
                return (parts[0][0] || '') + (parts[parts.length - 1][0] || '');
            }
            return name[0] || '';
        }

        // Computed properties
        const selectedChildrenCount = computed(() => selectedChildren.value.length);
        const playersTotal = computed(() => {
            if (!eventData.value) return 0;
            return selectedChildrenCount.value * (eventData.value.default_entry_fee || 0);
        });

        const grandTotal = computed(() => {
            const hotelTotal = priceCalc.priceBreakdown.value?.total || 0;
            return playersTotal.value + hotelTotal;
        });

        // Update checkout summary
        function updateCheckoutSummary() {
            // This will be called when children selection changes
            // Calculate totals, etc.
        }

        // Handle hotel room selector
        function openHotelRoomSelector() {
            if (selectedChildrenCount.value <= 0) {
                toast.show('Please select at least 1 player before adding a hotel stay.', 'warning');
                return;
            }
            showRoomModal.value = true;

            // Focus on modal when opened
            nextTick(() => {
                // Scroll to top immediately
                window.scrollTo(0, 0);
                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;

                // Scroll to top of iframe if in iframe
                if (window.parent && window.parent !== window) {
                    try {
                        window.parent.scrollTo({ top: 0, left: 0, behavior: 'instant' });
                        // Try to send message to parent to scroll
                        window.parent.postMessage({
                            type: 'nsc-scroll-to-top',
                            tabId: window.name || 'event-detail'
                        }, window.location.origin);
                    } catch (e) {
                        // Cross-origin, can't scroll parent
                    }
                }

                // Scroll to modal in current window
                const modalEl = document.querySelector('.room-selection-modal-fullscreen');
                if (modalEl) {
                    setTimeout(() => {
                        // Force scroll to top
                        modalEl.scrollTop = 0;
                        window.scrollTo(0, 0);
                        document.documentElement.scrollTop = 0;
                        document.body.scrollTop = 0;

                        // Try scrollIntoView as backup
                        modalEl.scrollIntoView({ behavior: 'auto', block: 'start', inline: 'nearest' });
                        modalEl.focus();
                    }, 50);
                }

                // Prevent body scroll
                document.body.style.overflow = 'hidden';
                document.documentElement.style.overflow = 'hidden';
            });
        }

        // Watch for modal close to restore scroll
        watch(() => showRoomModal.value, (isOpen) => {
            if (!isOpen) {
                // Restore body scroll when modal closes
                document.body.style.overflow = '';
            }
        });

        onMounted(() => {
            // Get hotel PK and event PK from element
            const appEl = document.querySelector('[id^="event-detail-app"]');
            if (appEl) {
                hotelPk.value = appEl.dataset.hotelPk || '';
                eventPkRef.value = appEl.dataset.eventPk || '';
            }
            loadEventData();
            loadRegistrantData();
            loadChildrenData();
            loadRooms();
        });

        // Expose methods for external access
        return {
            hotelPk,
            eventPk: eventPkRef,
            eventData,
            children,
            registrant,
            selectedChildren,
            selectedChildrenCount,
            playersTotal,
            reservation,
            priceCalc,
            toast,
            showRoomModal,
            showGuestModal,
            rooms,
            loading,
            handleSelectRoom,
            handleRemoveRoom,
            handleAddGuest,
            handleGuestDetailsContinue,
            handleContinueToCheckout,
            loadRooms,
            loadEventData,
            loadChildrenData,
            toggleChild,
            updateCheckoutSummary,
            openHotelRoomSelector,
            formatDate,
            formatPrice,
            formatLocation,
            getInitials,
            t: $t
        };
    },
    template: `
        <div v-if="eventData">
            <ToastComponent :toasts="toast.toasts" />

            <!-- Header -->
            <div class="tab-content-header mb-4" id="event-details-section" style="display: block !important; visibility: visible !important; opacity: 1 !important; width: 100% !important; position: relative !important; z-index: 1 !important;">
                <h4 style="color: var(--mlb-blue); font-weight: 800; font-size: 1.5rem; margin-bottom: 10px;">
                    <i class="fas fa-calendar-check me-2" style="color: var(--mlb-red);"></i>{{ t('eventDetails') }}
                </h4>
                <p class="text-muted">{{ t('eventInformationAndRegistration') }}</p>
            </div>

            <div class="row g-4" style="width: 100% !important; display: flex !important; flex-wrap: wrap !important; min-height: 400px !important; position: relative !important; z-index: 1 !important;">
                <!-- Left Side - Event Information -->
                <div class="col-lg-7">
                    <div class="event-info-card" style="background: white; border-radius: 16px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                        <!-- Banner/Logo -->
                        <div v-if="eventData.banner || eventData.logo" style="width: 100%; height: 300px; border-radius: 12px; overflow: hidden; margin-bottom: 25px;">
                            <img v-if="eventData.banner" :src="eventData.banner" :alt="eventData.title" style="width: 100%; height: 100%; object-fit: cover; object-position: center;">
                            <img v-else-if="eventData.logo" :src="eventData.logo" :alt="eventData.title" style="width: 100%; height: 100%; object-fit: contain; object-position: center; background: #f8f9fa;">
                        </div>

                        <!-- Title and Category -->
                        <div class="mb-4">
                            <span v-if="eventData.category" style="color: var(--mlb-red); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                {{ eventData.category.name }}
                            </span>
                            <h2 style="color: var(--mlb-blue); font-weight: 800; font-size: 2rem; margin-top: 10px; margin-bottom: 15px;">
                                {{ eventData.title }}
                            </h2>
                            <p v-if="eventData.event_type" style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0;">
                                <i class="fas fa-tag me-2" style="color: var(--mlb-red);"></i>{{ eventData.event_type.name }}
                            </p>
                        </div>

                        <!-- Separator Line -->
                        <div style="width: 100%; height: 2px; background: linear-gradient(90deg, var(--mlb-red) 0%, #b30029 100%); margin-bottom: 25px; border-radius: 2px;"></div>

                        <!-- Event Information -->
                        <div class="event-details mb-4">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 20px;">
                                <i class="fas fa-calendar-alt me-2" style="color: var(--mlb-red);"></i>{{ t('eventInformation') }}
                            </h5>
                            <div class="row g-3">
                                <!-- Left Column -->
                                <div class="col-md-6">
                                    <div class="d-flex flex-column" style="gap: 12px;">
                                        <!-- Date -->
                                        <div v-if="eventData.start_date">
                                            <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                                    <i class="fas fa-calendar" style="color: white; font-size: 1rem;"></i>
                                                </div>
                                                <div>
                                                    <div style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">{{ t('startDate') }}</div>
                                                    <div style="font-weight: 600; color: var(--mlb-blue);">{{ formatDate(eventData.start_date) }}</div>
                                                    <div v-if="eventData.end_date && eventData.end_date !== eventData.start_date" style="font-size: 0.75rem; color: #6c757d; margin-top: 2px;">
                                                        {{ t('endDate') }}: {{ formatDate(eventData.end_date) }}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Divisions -->
                                        <div v-if="eventData.divisions && eventData.divisions.length > 0">
                                            <div class="divisions-card" style="display: flex; align-items: flex-start; gap: 12px; padding: 14px; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border: 2px solid #e9ecef; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                                <div style="width: 44px; height: 44px; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 8px rgba(213, 0, 50, 0.2);">
                                                    <i class="fas fa-users" style="color: white; font-size: 1.1rem;"></i>
                                                </div>
                                                <div style="flex: 1; min-width: 0;">
                                                    <div class="divisions-title-desktop" style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 8px;">
                                                        {{ t('divisions') }} <span class="divisions-count">({{ eventData.divisions.length }})</span>
                                                    </div>
                                                    <div class="divisions-content" style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
                                                        <span v-for="(division, index) in eventData.divisions.slice(0, 3)" :key="division.id" class="division-badge" style="display: inline-flex; align-items: center; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; box-shadow: 0 2px 6px rgba(213, 0, 50, 0.25); white-space: nowrap; transition: all 0.2s;">
                                                            <i class="fas fa-tag" style="font-size: 0.65rem; margin-right: 5px; opacity: 0.9;"></i>
                                                            {{ division.name }}
                                                        </span>
                                                        <details v-if="eventData.divisions.length > 3" class="divisions-more">
                                                            <summary class="divisions-show-more-btn" style="display: inline-flex; align-items: center; gap: 5px; background: transparent; border: 1px solid var(--mlb-red); color: var(--mlb-red); padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; cursor: pointer; transition: all 0.2s; margin-top: 4px; pointer-events: auto !important; z-index: 100 !important; position: relative !important;">
                                                                <span class="divisions-show-more-text divisions-show-more-text--more">{{ t('showMore') }}</span>
                                                                <span class="divisions-show-more-text divisions-show-more-text--less">{{ t('showLess') }}</span>
                                                                <i class="fas fa-chevron-down divisions-show-more-chevron" style="font-size: 0.6rem; transition: transform 0.3s; transform: rotate(0deg);"></i>
                                                            </summary>
                                                            <div class="divisions-extra" style="display: flex; width: 100%; flex-wrap: wrap; gap: 6px; align-items: center; flex-direction: row;">
                                                                <span v-for="division in eventData.divisions.slice(3)" :key="division.id" class="division-badge" style="display: inline-flex; align-items: center; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; box-shadow: 0 2px 6px rgba(213, 0, 50, 0.25); white-space: nowrap; transition: all 0.2s;">
                                                                    <i class="fas fa-tag" style="font-size: 0.65rem; margin-right: 5px; opacity: 0.9;"></i>
                                                                    {{ division.name }}
                                                                </span>
                                                            </div>
                                                        </details>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Right Column -->
                                <div class="col-md-6">
                                    <div class="d-flex flex-column" style="gap: 12px;">
                                        <!-- Location -->
                                        <div v-if="formatLocation(eventData)">
                                            <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                                    <i class="fas fa-map-marker-alt" style="color: white; font-size: 1rem;"></i>
                                                </div>
                                                <div>
                                                    <div style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">{{ t('location') }}</div>
                                                    <div style="font-weight: 600; color: var(--mlb-blue);">{{ formatLocation(eventData) }}</div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Status -->
                                        <div>
                                            <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                                    <i class="fas fa-check-circle" style="color: white; font-size: 1rem;"></i>
                                                </div>
                                                <div>
                                                    <div style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">{{ t('status') }}</div>
                                                    <div style="font-weight: 600; color: var(--mlb-blue); text-transform: capitalize;">{{ eventData.status }}</div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Hotel -->
                                        <div v-if="eventData.hotel">
                                            <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                                                <div v-if="eventData.hotel.photo" style="width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0;">
                                                    <img :src="eventData.hotel.photo" :alt="eventData.hotel.name" style="width: 100%; height: 100%; object-fit: cover;">
                                                </div>
                                                <div v-else style="width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); display: flex; align-items: center; justify-content: center;">
                                                    <i class="fas fa-hotel" style="color: white; font-size: 1.5rem;"></i>
                                                </div>
                                                <div style="flex: 1;">
                                                    <div style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">{{ t('headquartersHotel') }}</div>
                                                    <div style="font-weight: 600; color: var(--mlb-blue);">{{ eventData.hotel.name }}</div>
                                                    <div v-if="eventData.hotel.address" style="font-size: 0.75rem; color: #6c757d; margin-top: 2px;">{{ eventData.hotel.address }}</div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Primary Site -->
                                        <div v-if="eventData.primary_site">
                                            <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                                                <div v-if="eventData.primary_site.image" style="width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0;">
                                                    <img :src="eventData.primary_site.image" :alt="eventData.primary_site.name" style="width: 100%; height: 100%; object-fit: cover;">
                                                </div>
                                                <div v-else style="width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); display: flex; align-items: center; justify-content: center;">
                                                    <i class="fas fa-map-marked-alt" style="color: white; font-size: 1.5rem;"></i>
                                                </div>
                                                <div style="flex: 1;">
                                                    <div style="font-size: 0.75rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">{{ t('primarySite') }}</div>
                                                    <div style="font-weight: 600; color: var(--mlb-blue);">{{ eventData.primary_site.name }}</div>
                                                    <div v-if="eventData.primary_site.address_1" style="font-size: 0.75rem; color: #6c757d; margin-top: 2px;">
                                                        {{ eventData.primary_site.address_1 }}<span v-if="eventData.primary_site.address_2">, {{ eventData.primary_site.address_2 }}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Video -->
                        <div v-if="eventData.video_url" class="mb-4" style="margin-top: 30px;">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 20px;">
                                <i class="fas fa-video me-2" style="color: var(--mlb-red);"></i>{{ t('eventVideo') }}
                            </h5>
                            <div id="event-video-container" style="position: relative; width: 100%; padding-bottom: 56.25%; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.15); background: #000;">
                                <!-- Video will be embedded here by JavaScript -->
                            </div>
                        </div>

                        <!-- Separator Line -->
                        <div v-if="eventData.video_url || eventData.description" style="width: 100%; height: 2px; background: linear-gradient(90deg, var(--mlb-red) 0%, #b30029 100%); margin-bottom: 25px; margin-top: 25px; border-radius: 2px;"></div>

                        <!-- Description -->
                        <div v-if="eventData.description" class="mb-4">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 15px;">
                                <i class="fas fa-info-circle me-2" style="color: var(--mlb-red);"></i>{{ t('description') }}
                            </h5>
                            <div style="color: #333; line-height: 1.8; font-size: 0.95rem; font-weight: normal;" class="event-description" v-html="eventData.description"></div>
                        </div>

                        <!-- External Link -->
                        <div v-if="eventData.external_link" class="mt-4">
                            <a :href="eventData.external_link" target="_blank" class="btn" style="background: var(--mlb-blue); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px;">
                                <i class="fas fa-external-link-alt"></i>{{ t('moreInformation') }}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Right Side - Checkout -->
                <div class="col-lg-5">
                    <div class="checkout-card" style="background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: sticky; top: 20px;">
                        <h4 style="color: var(--mlb-blue); font-weight: 800; margin-bottom: 18px; border-bottom: 3px solid var(--mlb-red); padding-bottom: 12px; font-size: 1.2rem;">
                            <i class="fas fa-shopping-cart me-2" style="color: var(--mlb-red);"></i>{{ t('checkout') }}
                        </h4>

                        <!-- Step 1: Select Players -->
                        <div v-if="children && children.length > 0" class="checkout-step mb-4" id="step-players">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 12px; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                                <span style="background: var(--mlb-red); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700;">1</span>
                                <i class="fas fa-users me-1" style="color: var(--mlb-red);"></i>{{ t('selectPlayers') }}
                            </h5>
                            <div class="children-list">
                                <div v-for="child in children" :key="child.id" class="child-item mb-2"
                                     :style="{
                                         border: '2px solid ' + (child.registered ? '#28a745' : '#e9ecef'),
                                         borderRadius: '8px',
                                         padding: '10px',
                                         transition: 'all 0.3s',
                                         cursor: child.registered ? 'not-allowed' : 'pointer',
                                         background: child.registered ? '#f8fff9' : 'transparent'
                                     }">
                                    <div class="form-check" style="display: flex; align-items: center; gap: 10px;">
                                        <input v-if="!child.registered"
                                               class="form-check-input child-checkbox"
                                               type="checkbox"
                                               :value="child.id"
                                               :id="'child_' + child.id"
                                               :checked="selectedChildren.includes(child.id)"
                                               @change="toggleChild(child.id)"
                                               style="width: 18px; height: 18px; cursor: pointer; margin: 0; flex-shrink: 0;">
                                        <input v-else
                                               class="form-check-input child-checkbox"
                                               type="checkbox"
                                               :value="child.id"
                                               :id="'child_' + child.id"
                                               disabled
                                               style="width: 18px; height: 18px; cursor: not-allowed; margin: 0; flex-shrink: 0; opacity: 0.5;">
                                        <label :for="'child_' + child.id"
                                               :style="{ cursor: child.registered ? 'not-allowed' : 'pointer', width: '100%', margin: 0, opacity: child.registered ? 0.7 : 1 }">
                                            <div style="display: flex; align-items: center; gap: 10px;">
                                                <!-- Photo or Initials -->
                                                <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%);">
                                                    <img v-if="child.profile_picture" :src="child.profile_picture" :alt="child.name" style="width: 100%; height: 100%; object-fit: cover;">
                                                    <span v-else-if="getInitials(child.name)" style="color: white; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                                        {{ getInitials(child.name) }}
                                                    </span>
                                                    <i v-else class="fas fa-user" style="color: white; font-size: 1rem;"></i>
                                                </div>
                                                <!-- Player Information -->
                                                <div style="flex: 1; min-width: 0;">
                                                    <div style="font-weight: 700; color: var(--mlb-blue); font-size: 0.9rem; line-height: 1.2; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                                        <span>{{ child.name }}</span>
                                                        <span v-if="child.registered" style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                                                            <i class="fas fa-check-circle" style="font-size: 0.65rem;"></i>{{ t('registered') }}
                                                        </span>
                                                    </div>
                                                    <div v-if="child.division" style="font-size: 0.75rem; color: #6c757d; margin-top: 2px;">
                                                        <i class="fas fa-tag me-1" style="color: var(--mlb-red); font-size: 0.65rem;"></i>{{ child.division }}
                                                    </div>
                                                </div>
                                                <!-- Price -->
                                                <div v-if="!child.registered" class="child-price" style="font-weight: 700; color: var(--mlb-red); font-size: 0.95rem; flex-shrink: 0;">
                                                    {{ formatPrice(eventData.default_entry_fee) }}
                                                </div>
                                                <div v-else style="font-weight: 600; color: #6c757d; font-size: 0.85rem; flex-shrink: 0; font-style: italic;">
                                                    {{ t('alreadyRegistered') }}
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Step 2: Add Hotel Stay -->
                        <div v-if="eventData.hotel" class="checkout-step mb-4" id="step-hotel">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 12px; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                                <span style="background: var(--mlb-red); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700;">2</span>
                                <i class="fas fa-hotel me-1" style="color: var(--mlb-red);"></i>{{ t('addHotelStay') }}
                            </h5>
                            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border: 2px solid #e9ecef; border-radius: 12px; padding: 12px;">
                                <div style="font-size: 0.8rem; color: #6c757d; font-weight: 600; line-height: 1.25; margin-bottom: 10px;">
                                    {{ t('hotelBuyOutFeeMessage') }}
                                </div>
                            </div>
                            <button type="button"
                                    class="btn btn-sm w-100"
                                    id="add-hotel-stay-btn"
                                    @click="openHotelRoomSelector"
                                    style="background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); color: white; padding: 10px; border-radius: 10px; font-weight: 800; font-size: 0.9rem; border: none; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 8px; margin-top: 10px;"
                                    @mouseover="$event.target.style.transform='translateY(-1px)'; $event.target.style.boxShadow='0 10px 24px rgba(213, 0, 50, 0.25)';"
                                    @mouseout="$event.target.style.transform='translateY(0)'; $event.target.style.boxShadow='none';">
                                <i class="fas fa-hotel"></i>
                                <span>{{ t('addHotelStay') }}</span>
                            </button>
                        </div>

                        <!-- Order Summary -->
                        <div class="checkout-summary" style="border-top: 3px solid var(--mlb-red); padding-top: 20px; margin-top: 20px;">
                            <h5 style="color: var(--mlb-blue); font-weight: 700; margin-bottom: 15px; font-size: 1rem;">
                                <i class="fas fa-receipt me-2" style="color: var(--mlb-red);"></i>{{ t('orderSummary') }}
                            </h5>

                            <!-- Players Summary -->
                            <div v-if="selectedChildrenCount > 0" id="checkout-players-summary" style="margin-bottom: 15px;">
                                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border: 2px solid #e9ecef; border-radius: 12px; padding: 15px; border-left: 4px solid var(--mlb-blue);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="flex: 1;">
                                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                                <i class="fas fa-users" style="color: var(--mlb-blue); font-size: 1rem;"></i>
                                                <span style="font-weight: 700; color: var(--mlb-blue); font-size: 1rem;">
                                                    {{ selectedChildrenCount }} {{ t('players') }}
                                                </span>
                                            </div>
                                            <div style="font-size: 0.75rem; color: #6c757d;">{{ t('eventRegistration') }}</div>
                                        </div>
                                        <div style="text-align: right; flex-shrink: 0; margin-left: 15px;">
                                            <div style="font-weight: 800; color: var(--mlb-blue); font-size: 1.2rem;">{{ formatPrice(playersTotal) }}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Hotel Summary -->
                            <div v-if="reservation.state.rooms.length > 0" id="checkout-hotel-summary" style="margin-bottom: 15px;">
                                <div style="background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%); border: 2px solid #fecaca; border-radius: 12px; padding: 15px; border-left: 4px solid var(--mlb-red);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="flex: 1;">
                                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                                <i class="fas fa-hotel" style="color: var(--mlb-red); font-size: 1rem;"></i>
                                                <span style="font-weight: 700; color: var(--mlb-red); font-size: 1rem;">
                                                    {{ reservation.state.rooms.length }} {{ reservation.state.rooms.length === 1 ? t('room') : t('rooms') }}
                                                </span>
                                            </div>
                                            <div style="font-size: 0.75rem; color: #6c757d;">{{ t('hotelStay') }}</div>
                                        </div>
                                        <div style="text-align: right; flex-shrink: 0; margin-left: 15px;">
                                            <div style="font-weight: 800; color: var(--mlb-red); font-size: 1.2rem;">{{ formatPrice(priceCalc.priceBreakdown.value?.total || 0) }}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Total -->
                            <div style="border-top: 2px solid var(--mlb-red); padding-top: 15px; margin-top: 15px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 800; color: var(--mlb-blue); font-size: 1.1rem;">{{ t('total') }}:</span>
                                    <span style="font-weight: 800; color: var(--mlb-red); font-size: 1.4rem;">{{ formatPrice(grandTotal) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modals -->
            <RoomSelectionModal
                v-if="hotelPk"
                :hotel-pk="hotelPk"
                :rooms="rooms || []"
                :selected-rooms="reservation.state.rooms || []"
                :guests="reservation.state.guests || []"
                :children="children || []"
                :selected-children="selectedChildren || []"
                :registrant="registrant"
                :show="showRoomModal"
                @close="showRoomModal = false"
                @select-room="handleSelectRoom"
                @remove-room="handleRemoveRoom"
                @add-guest="handleAddGuest"
            />

            <GuestDetailsModal
                v-if="hotelPk"
                :hotel-pk="hotelPk"
                :guests="reservation.state.guests"
                :show="showGuestModal"
                @close="showGuestModal = false"
                @continue="handleGuestDetailsContinue"
            />
        </div>
        <div v-else>
            <div style="text-align: center; padding: 40px;">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: var(--mlb-blue);"></i>
                <p style="margin-top: 20px; color: #6c757d;">{{ t('loading') }}</p>
            </div>
        </div>
    `
};

// Export for use
window.EventDetailApp = EventDetailApp;

