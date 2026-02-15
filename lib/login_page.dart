import 'dart:math';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter/foundation.dart'; // for kIsWeb
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:hacker/dashboard_page.dart';

// ── Color Palette (same as cover_page.dart) ─────────────────────────────────
const _kBgDark = Color(0xFF0B1020);
const _kBgCard = Color(0xFF131A2B);
const _kBgCardLight = Color(0xFF1B243A);
const _kGreen = Color(0xFF5B8CFF);
const _kGreenGlow = Color(0x1F5B8CFF);
const _kTextPrimary = Color(0xFFF2F5FF);
const _kTextSecondary = Color(0xFFA8B3CF);
const _kBorderGreen = Color(0xFF33415F);

// ════════════════════════════════════════════════════════════════════════════
//  LOGIN PAGE
// ════════════════════════════════════════════════════════════════════════════
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  late final AnimationController _bgCtrl;

  bool _isLogin = true;
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _bgCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    )..repeat();
  }

  @override
  void dispose() {
    _bgCtrl.dispose();
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _authenticate() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      if (_isLogin) {
        await FirebaseAuth.instance.signInWithEmailAndPassword(
          email: _emailController.text.trim(),
          password: _passwordController.text.trim(),
        );
      } else {
        final credential =
            await FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: _emailController.text.trim(),
          password: _passwordController.text.trim(),
        );

        if (credential.user != null) {
          await credential.user!
              .updateDisplayName(_nameController.text.trim());

          await FirebaseFirestore.instance
              .collection('users')
              .doc(credential.user!.uid)
              .set({
            'name': _nameController.text.trim(),
            'email': credential.user!.email,
            'role': 'user',
            'created_at': FieldValue.serverTimestamp(),
            'last_login': FieldValue.serverTimestamp(),
          });
        }
      }

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const DashboardPage()),
        );
      }
    } on FirebaseAuthException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } on FirebaseException catch (e) {
      String msg = 'Firestore Error: ${e.message}';
      if (e.code == 'permission-denied') {
        msg +=
            '\n\nRunning locally? Make sure you have deployed your "firestore.rules" to the Firebase Console!';
      }
      if (mounted) setState(() => _errorMessage = msg);
    } catch (e) {
      if (mounted) {
        setState(() => _errorMessage = 'An unexpected error occurred: $e');
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final GoogleSignIn googleSignIn = GoogleSignIn(
        clientId: kIsWeb ? dotenv.env['WEB_GOOGLE_CLIENT_ID'] : null,
      );
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      if (googleUser == null) {
        return; // User canceled
      }

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      final OAuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final UserCredential userCredential =
          await FirebaseAuth.instance.signInWithCredential(credential);

      if (userCredential.user != null) {
        // Fetch and cache Google profile image as Base64 to avoid 429 errors
        String? base64Image;
        if (userCredential.user!.photoURL != null) {
          try {
            final response = await http.get(Uri.parse(userCredential.user!.photoURL!));
            if (response.statusCode == 200) {
              base64Image = base64Encode(response.bodyBytes);
            }
          } catch (e) {
            debugPrint('Error fetching Google profile image: $e');
          }
        }

        // Create/Update user in Firestore
        await FirebaseFirestore.instance
            .collection('users')
            .doc(userCredential.user!.uid)
            .set({
          'name': userCredential.user!.displayName,
          'email': userCredential.user!.email,
          'role': 'user',
          'last_login': FieldValue.serverTimestamp(),
          if (base64Image != null) 'photo_base64': base64Image,
        }, SetOptions(merge: true));
      }

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const DashboardPage()),
        );
      }
    } on FirebaseAuthException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = 'Google Sign-In failed: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final isWide = w > 800;

    return Scaffold(
      backgroundColor: _kBgDark,
      body: Stack(
        children: [
          // ── Animated Background (identical to cover page) ──────────────
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _bgCtrl,
              builder: (context, _) {
                final t = _bgCtrl.value * 2 * pi;
                return Stack(
                  children: [
                    Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin:
                              Alignment(-0.2 + sin(t * 0.3) * 0.25, -1),
                          end: Alignment(
                              0.2 + cos(t * 0.25) * 0.25, 1),
                          colors: const [
                            Color(0xFF0B1020),
                            Color(0xFF0A0F1D),
                            Color(0xFF080C18),
                          ],
                        ),
                      ),
                    ),
                    Positioned(
                      top: -120 + sin(t) * 28,
                      right: -80 + cos(t * 0.9) * 36,
                      child: Container(
                        width: 320,
                        height: 320,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0x365B8CFF),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 280 + cos(t * 1.1) * 24,
                      left: -120 + sin(t * 0.8) * 30,
                      child: Container(
                        width: 260,
                        height: 260,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0x285B8CFF),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 140 + sin(t * 1.5) * 18,
                      left: 420 + cos(t * 1.2) * 24,
                      child: Container(
                        width: 180,
                        height: 180,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0x1F8B5CF6),
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: -100 + cos(t * 1.3) * 20,
                      right: 260 + sin(t * 0.7) * 26,
                      child: Container(
                        width: 220,
                        height: 220,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Color(0x1B38BDF8),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),

          // ── Content ────────────────────────────────────────────────────
          Center(
            child: SingleChildScrollView(
              padding: EdgeInsets.symmetric(
                horizontal: isWide ? 80 : 24,
                vertical: 40,
              ),
              child: isWide
                  ? _buildWideLayout()
                  : _buildNarrowLayout(),
            ),
          ),
        ],
      ),
    );
  }

  // ── Wide Layout (side-by-side branding + form) ─────────────────────────
  Widget _buildWideLayout() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // Left: Branding
        Expanded(
          flex: 5,
          child: _buildBranding(),
        ),
        const SizedBox(width: 60),
        // Right: Form Card
        Expanded(
          flex: 4,
          child: _buildFormCard(),
        ),
      ],
    );
  }

  // ── Narrow Layout (stacked) ────────────────────────────────────────────
  Widget _buildNarrowLayout() {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 440),
      child: Column(
        children: [
          _buildBrandingCompact(),
          const SizedBox(height: 32),
          _buildFormCard(),
        ],
      ),
    );
  }

  // ── Branding Panel (wide) ──────────────────────────────────────────────
  Widget _buildBranding() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'HackHub',
          style: GoogleFonts.outfit(
            fontSize: 56,
            fontWeight: FontWeight.w800,
            color: _kTextPrimary,
            letterSpacing: -1,
            height: 1.1,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          _isLogin
              ? 'Welcome back,\nready to build?'
              : 'Join the community\nof hackers.',
          style: GoogleFonts.outfit(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: _kTextPrimary.withValues(alpha: 0.85),
            height: 1.3,
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Discover repos, collaborate on issues, enhance READMEs with AI, '
          'and find like-minded hackers for your next big project.',
          style: GoogleFonts.inter(
            fontSize: 15,
            color: _kTextSecondary,
            height: 1.7,
          ),
        ),
        const SizedBox(height: 36),
        // Stats row
        Wrap(
          spacing: 32,
          runSpacing: 16,
          children: [
            _statChip('50K+', 'REPOS INDEXED'),
            _statChip('10+', 'SMART FILTERS'),
            _statChip('24/7', 'ALWAYS ONLINE'),
          ],
        ),
      ],
    );
  }

  // ── Branding Panel (compact / mobile) ──────────────────────────────────
  Widget _buildBrandingCompact() {
    return Column(
      children: [
        Text(
          'HackHub',
          style: GoogleFonts.outfit(
            fontSize: 40,
            fontWeight: FontWeight.w800,
            color: _kTextPrimary,
            letterSpacing: -1,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          _isLogin ? 'Welcome back' : 'Create your account',
          style: GoogleFonts.inter(
            fontSize: 16,
            color: _kTextSecondary,
          ),
        ),
      ],
    );
  }

  // ── Form Card ──────────────────────────────────────────────────────────
  Widget _buildFormCard() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 460),
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: _kBgCard,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _kBorderGreen),
        boxShadow: const [
          BoxShadow(
            color: Color(0x22000000),
            blurRadius: 24,
            offset: Offset(0, 14),
          ),
        ],
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Mac-style dots ─────────────────────────────────────────
            Row(
              children: [
                _dot(const Color(0xFFFF5F57)),
                const SizedBox(width: 6),
                _dot(const Color(0xFFFFBD2E)),
                const SizedBox(width: 6),
                _dot(const Color(0xFF28C840)),
                const Spacer(),
                Text(
                  _isLogin ? 'Sign In' : 'Sign Up',
                  style: GoogleFonts.inter(
                    color: _kTextSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 28),

            // ── Title ──────────────────────────────────────────────────
            Text(
              _isLogin ? 'Welcome Back' : 'Create Account',
              style: GoogleFonts.outfit(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: _kTextPrimary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 6),
            Text(
              _isLogin ? 'Sign in to continue' : 'Join us today',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: _kTextSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),

            // ── Fields ─────────────────────────────────────────────────
            if (!_isLogin) ...[
              _buildInputField(
                controller: _nameController,
                label: 'Full Name',
                icon: Icons.person_outline,
                validator: (v) =>
                    (v == null || v.isEmpty) ? 'Please enter your name' : null,
              ),
              const SizedBox(height: 14),
            ],
            _buildInputField(
              controller: _emailController,
              label: 'Email Address',
              icon: Icons.email_outlined,
              keyboardType: TextInputType.emailAddress,
              validator: (v) =>
                  (v == null || v.isEmpty || !v.contains('@'))
                      ? 'Please enter a valid email'
                      : null,
            ),
            const SizedBox(height: 14),
            _buildInputField(
              controller: _passwordController,
              label: 'Password',
              icon: Icons.lock_outline,
              obscureText: _obscurePassword,
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword
                      ? Icons.visibility_off_outlined
                      : Icons.visibility_outlined,
                  color: _kTextSecondary,
                  size: 20,
                ),
                onPressed: () =>
                    setState(() => _obscurePassword = !_obscurePassword),
              ),
              validator: (v) => (v == null || v.length < 6)
                  ? 'Password must be at least 6 characters'
                  : null,
            ),
            const SizedBox(height: 24),

            // ── Error Message ──────────────────────────────────────────
            if (_errorMessage != null) ...[
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: const Color(0x20FF5252),
                  border: Border.all(color: const Color(0x44FF5252)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline,
                        color: Color(0xFFFF5252), size: 18),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: GoogleFonts.inter(
                          color: const Color(0xFFFF8A80),
                          fontSize: 13,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // ── Submit Button ──────────────────────────────────────────
            _GlowButton(
              label: _isLogin ? 'Sign In' : 'Sign Up',
              icon: _isLogin ? Icons.login : Icons.person_add,
              isLoading: _isLoading,
              onTap: _authenticate,
            ),
            const SizedBox(height: 16),
            _GoogleButton(
              onTap: _signInWithGoogle,
              isLoading: _isLoading,
            ),
            const SizedBox(height: 20),

            // ── Toggle ─────────────────────────────────────────────────
            Center(
              child: GestureDetector(
                onTap: () {
                  setState(() {
                    _isLogin = !_isLogin;
                    _errorMessage = null;
                    _formKey.currentState?.reset();
                  });
                },
                child: RichText(
                  text: TextSpan(
                    style: GoogleFonts.inter(fontSize: 14),
                    children: [
                      TextSpan(
                        text: _isLogin
                            ? "Don't have an account? "
                            : 'Already have an account? ',
                        style: const TextStyle(color: _kTextSecondary),
                      ),
                      TextSpan(
                        text: _isLogin ? 'Sign Up' : 'Login',
                        style: const TextStyle(
                          color: _kGreen,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Input Field ────────────────────────────────────────────────────────
  Widget _buildInputField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
    bool obscureText = false,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: _kBgCardLight,
        borderRadius: BorderRadius.circular(14),
      ),
      child: TextFormField(
        controller: controller,
        style: GoogleFonts.inter(color: _kTextPrimary, fontSize: 14),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: GoogleFonts.inter(color: _kTextSecondary, fontSize: 14),
          prefixIcon: Icon(icon, color: _kTextSecondary, size: 20),
          suffixIcon: suffixIcon,
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: _kBorderGreen),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: _kGreen, width: 1.5),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFFF5252)),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFFF5252)),
          ),
          filled: true,
          fillColor: Colors.transparent,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        ),
        keyboardType: keyboardType,
        obscureText: obscureText,
        validator: validator,
      ),
    );
  }

  // ── Helpers ────────────────────────────────────────────────────────────
  Widget _dot(Color color) {
    return Container(
      width: 10,
      height: 10,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
    );
  }

  Widget _statChip(String value, String label) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: GoogleFonts.outfit(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: _kTextPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            color: _kTextSecondary,
            letterSpacing: 1.5,
          ),
        ),
      ],
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  GLOW BUTTON (matches cover page _HeroButton)
// ════════════════════════════════════════════════════════════════════════════
class _GlowButton extends StatefulWidget {
  const _GlowButton({
    required this.label,
    required this.icon,
    required this.onTap,
    this.isLoading = false,
  });
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final bool isLoading;

  @override
  State<_GlowButton> createState() => _GlowButtonState();
}

class _GlowButtonState extends State<_GlowButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: widget.isLoading ? null : widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: _kGreen,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: _kGreen.withValues(alpha: _hovering ? 0.3 : 0.15),
                blurRadius: _hovering ? 20 : 10,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: widget.isLoading
              ? const Center(
                  child: SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: _kBgDark,
                    ),
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(widget.icon, size: 18, color: _kBgDark),
                    const SizedBox(width: 10),
                    Text(
                      widget.label,
                      style: GoogleFonts.inter(
                        color: _kBgDark,
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class _GoogleButton extends StatefulWidget {
  const _GoogleButton({required this.onTap, this.isLoading = false});
  final VoidCallback onTap;
  final bool isLoading;

  @override
  State<_GoogleButton> createState() => _GoogleButtonState();
}

class _GoogleButtonState extends State<_GoogleButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: widget.isLoading ? null : widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: _kBgCardLight,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: _hovering ? _kTextPrimary : _kBorderGreen,
            ),
            boxShadow: [
              if (_hovering)
                const BoxShadow(
                  color: Color(0x1FFFFFFF),
                  blurRadius: 12,
                  offset: Offset(0, 4),
                ),
            ],
          ),
          child: widget.isLoading
              ? const Center(
                  child: SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: _kTextPrimary,
                    ),
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Simple G icon
                    Container(
                      padding: const EdgeInsets.all(2),
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.g_mobiledata,
                          color: Colors.black, size: 16),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      'Sign in with Google',
                      style: GoogleFonts.inter(
                        color: _kTextPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}
