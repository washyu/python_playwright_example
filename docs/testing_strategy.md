# Testing Strategy - Sauce Demo

## Current Test Coverage

### ✅ Implemented Tests
**test_login.py**
- `test_login()` - Successful login with standard_user
- `test_blocked_login()` - Blocked user (locked_out_user) login attempt

### ✅ Existing Page Classes
- `LoginPage` - Login page interactions
- `InventoryPage` - Product listing page (basic)

### ❌ Missing Page Classes
- `CartPage` - Shopping cart page
- `ProductDetailsPage` - Individual product detail page
- `CheckoutStepOnePage` - Customer information form
- `CheckoutStepTwoPage` - Order overview/summary
- `CheckoutCompletePage` - Order confirmation page

---

## Test Scenarios by Category

## 1. Authentication Tests
**File:** `test_login.py` (expand existing)
**Page Classes:** LoginPage

### Current Coverage
- ✅ Valid login (standard_user)
- ✅ Locked out user

### To Implement
- ✅ Invalid username
- ✅ Invalid password
- ✅ Empty username
- ✅ Empty password
- ✅ Empty username and password
- ✅ Case sensitivity verification
- ✅ SQL injection attempt (security test)
- ✅ XSS attempt in login fields (security test)

---

## 2. Logout Tests
**File:** `test_logout.py` (new)
**Page Classes:** LoginPage, InventoryPage

### To Implement
- ✅ Successful logout from inventory page
- ✅ Cannot access inventory after logout (session cleared)
- ✅ Login again after logout
- [ ] Logout from different pages (cart, checkout)

---

## 3. Inventory/Product Listing Tests
**File:** `test_inventory.py` (new)
**Page Classes:** InventoryPage (needs expansion)

### To Implement
- [ ] All 6 products are displayed
- [ ] Product images are loaded
- [ ] Product names are displayed correctly
- [ ] Product descriptions are present
- [ ] Product prices are displayed and formatted correctly
- [ ] "Add to cart" buttons are visible for all products
- [ ] Product sorting:
  - [ ] Name (A to Z)
  - [ ] Name (Z to A)
  - [ ] Price (low to high)
  - [ ] Price (high to low)
  - [ ] Verify product order changes after sorting

---

## 4. Product Details Tests
**File:** `test_product_details.py` (new)
**Page Classes:** InventoryPage, ProductDetailsPage ⚠️ (needs creation)

### To Implement
- [ ] Click product name navigates to detail page
- [ ] Click product image navigates to detail page
- [ ] Product details page shows correct information:
  - [ ] Product name
  - [ ] Product description
  - [ ] Product price
  - [ ] Product image
- [ ] "Back to products" button returns to inventory
- [ ] "Add to cart" from product details page
- [ ] "Remove" from product details page (if already in cart)

---

## 5. Shopping Cart Tests
**File:** `test_cart.py` (new)
**Page Classes:** InventoryPage, CartPage ⚠️ (needs creation)

### To Implement
- [ ] Add single product to cart from inventory
- [ ] Add multiple products to cart
- [ ] Cart badge shows correct item count (1, 2, 3+)
- [ ] Remove product from inventory page (button changes to "Add to cart")
- [ ] Click cart icon navigates to cart page
- [ ] Cart page displays correct products
- [ ] Cart shows correct product names, descriptions, prices
- [ ] Remove product from cart page
- [ ] Remove all products from cart
- [ ] "Continue shopping" button returns to inventory
- [ ] Empty cart shows no items
- [ ] Cart badge disappears when empty

---

## 6. Checkout Tests
**File:** `test_checkout.py` (new)
**Page Classes:** CartPage ⚠️, CheckoutStepOnePage ⚠️, CheckoutStepTwoPage ⚠️, CheckoutCompletePage ⚠️ (need creation)

### To Implement

#### Checkout Step 1 - Customer Information
- [ ] Click "Checkout" from cart with items
- [ ] Cannot proceed without items in cart
- [ ] Fill checkout form with valid information:
  - [ ] First name
  - [ ] Last name
  - [ ] Postal code
- [ ] Form validation:
  - [ ] Missing first name shows error
  - [ ] Missing last name shows error
  - [ ] Missing postal code shows error
  - [ ] Error message displayed for each field
- [ ] "Cancel" button returns to cart
- [ ] "Continue" button proceeds to overview

#### Checkout Step 2 - Overview
- [ ] Overview displays correct items
- [ ] Overview shows correct quantities
- [ ] Overview shows correct prices
- [ ] Item total is correct (sum of products)
- [ ] Tax calculation is correct
- [ ] Total (item total + tax) is correct
- [ ] Payment and shipping info displayed
- [ ] "Cancel" button returns to inventory
- [ ] "Finish" button completes purchase

#### Checkout Complete
- [ ] Success message displayed after purchase
- [ ] Order confirmation image/icon displayed
- [ ] "Back Home" button displayed
- [ ] "Back Home" button returns to inventory
- [ ] Cart is cleared after successful purchase
- [ ] Cart badge is removed after purchase

---

## 7. Navigation Tests
**File:** `test_navigation.py` (new)
**Page Classes:** All pages

### To Implement
- [ ] Hamburger menu opens
- [ ] Hamburger menu closes (X button)
- [ ] Hamburger menu closes (click outside)
- [ ] Menu links:
  - [ ] "All Items" navigates to inventory
  - [ ] "About" navigates to Sauce Labs website (external)
  - [ ] "Logout" logs user out
  - [ ] "Reset App State" clears cart
- [ ] Cart icon is visible on all pages
- [ ] Cart icon click navigates to cart from any page
- [ ] Browser back button behavior:
  - [ ] From inventory to login (should redirect to inventory if logged in)
  - [ ] From cart to inventory
  - [ ] From product details to inventory
  - [ ] From checkout back to cart

---

## 8. Visual/UI Tests
**File:** `test_ui.py` (new)
**Page Classes:** All pages

### To Implement
- [ ] Login page layout
- [ ] Inventory page layout
- [ ] Header is present on all pages
- [ ] Footer is present on all pages
- [ ] Footer links:
  - [ ] Twitter link
  - [ ] Facebook link
  - [ ] LinkedIn link
- [ ] Images load properly (except for problem_user)
- [ ] Shopping cart badge appearance:
  - [ ] Not visible when cart is empty
  - [ ] Appears when items added
  - [ ] Shows correct number
- [ ] Logo/brand present

---

## 9. Problem User Tests
**File:** `test_problem_user.py` (new)
**Page Classes:** LoginPage, InventoryPage

### To Implement
- [ ] Login as problem_user
- [ ] Product images fail to load or show incorrect images
- [ ] Document specific issues with problem_user
- [ ] Verify other functionality still works

---

## 10. Performance Tests
**File:** `test_performance.py` (new)
**Page Classes:** LoginPage, InventoryPage

### To Implement
- [ ] Login as performance_glitch_user
- [ ] Login takes longer than standard_user
- [ ] Operations are slower
- [ ] Measure and assert page load times
- [ ] Compare performance vs standard_user

---

## 11. End-to-End Journey Tests
**File:** `test_e2e.py` (new)
**Page Classes:** All pages

### Complete User Journeys
- [ ] Happy path: Login → Browse → Add to cart → Checkout → Complete
- [ ] Browse and abandon: Login → Browse → Add to cart → Logout
- [ ] Multiple items: Login → Add multiple items → Checkout → Complete
- [ ] Change mind: Login → Add items → Remove some → Checkout → Complete
- [ ] Window shopping: Login → Browse products → View details → Logout (no purchase)

---

## 12. Cross-Browser Tests
**Configuration:** Run critical tests across browsers
**Browsers:** Chromium (default), Firefox, WebKit

### To Implement
- [ ] Configure pytest to run smoke tests in all browsers
- [ ] Login test in all browsers
- [ ] Complete checkout in all browsers
- [ ] Cart operations in all browsers

---

## 13. Mobile/Responsive Tests
**File:** `test_mobile.py` (new)
**Configuration:** Mobile viewport sizes

### To Implement
- [ ] Login on mobile viewport (iPhone, Android)
- [ ] Navigation menu on mobile
- [ ] Product browsing on mobile
- [ ] Cart operations on mobile
- [ ] Checkout flow on mobile
- [ ] Verify responsive layout

---

## 14. Error User Tests
**File:** `test_error_user.py` (new)
**Page Classes:** All pages

### To Implement
- [ ] Login as error_user
- [ ] Identify specific errors that occur
- [ ] Cart operations fail
- [ ] Checkout operations fail
- [ ] Document error_user behavior

---

## 15. Visual User Tests
**File:** `test_visual_user.py` (new)
**Page Classes:** All pages

### To Implement
- [ ] Login as visual_user
- [ ] Verify visual differences/bugs
- [ ] Compare layout to standard_user
- [ ] Document visual issues

---

## Implementation Priority

### 🔴 High Priority (Critical User Flows)
1. **Shopping Cart Tests** - Core e-commerce functionality
2. **Checkout Tests** - Revenue-critical path
3. **Inventory Tests** - Product browsing and sorting
4. **End-to-End Tests** - Complete user journeys

### 🟡 Medium Priority (Important Features)
5. **Product Details Tests** - Product information
6. **Navigation Tests** - User experience
7. **Logout Tests** - Session management
8. **Authentication Tests** - Expand coverage

### 🟢 Low Priority (Edge Cases & Nice-to-Have)
9. **UI Tests** - Visual validation
10. **Cross-Browser Tests** - Compatibility
11. **Mobile Tests** - Responsive design
12. **Special User Tests** - problem_user, error_user, visual_user
13. **Performance Tests** - Non-functional testing

---

## Page Class Requirements Summary

### To Implement (Priority Order)
1. **CartPage** - Required for cart and checkout tests
2. **CheckoutStepOnePage** - Customer information form
3. **CheckoutStepTwoPage** - Order overview
4. **CheckoutCompletePage** - Order confirmation
5. **ProductDetailsPage** - Individual product page

### To Expand
- **InventoryPage** - Add methods for:
  - Sorting products
  - Adding products to cart by name/index
  - Removing products from cart
  - Clicking product names/images
  - Getting product details

---

## Test Data

### Valid Users
- `standard_user` / `secret_sauce` - Normal user
- `problem_user` / `secret_sauce` - Images broken
- `performance_glitch_user` / `secret_sauce` - Slow operations
- `error_user` / `secret_sauce` - Errors occur
- `visual_user` / `secret_sauce` - Visual bugs

### Invalid Users
- `locked_out_user` / `secret_sauce` - Blocked
- Any invalid username/password combinations

### Test Products (6 total on site)
- Sauce Labs Backpack - $29.99
- Sauce Labs Bike Light - $9.99
- Sauce Labs Bolt T-Shirt - $15.99
- Sauce Labs Fleece Jacket - $49.99
- Sauce Labs Onesie - $7.99
- Test.allTheThings() T-Shirt (Red) - $15.99

### Test Checkout Data
```python
VALID_CHECKOUT_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "postal_code": "12345"
}
```

---

## Notes
- All tests should run in both headed and headless mode
- Use environment variables for test configuration (.env file)
- HTML reports generated automatically
- GitHub Actions runs tests on push/PR
- Focus on creating robust page classes before implementing tests
