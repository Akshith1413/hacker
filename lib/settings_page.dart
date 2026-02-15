import 'dart:convert';
import 'dart:io';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:hacker/login_page.dart';

// ── Color Constants (reused for consistency) ───────────────────────────────
const _kBgDark = Color(0xFF0B1020);
const _kBgCard = Color(0xFF131A2B);
const _kGreen = Color(0xFF5B8CFF);
const _kTextPrimary = Color(0xFFF2F5FF);
const _kTextSecondary = Color(0xFFA8B3CF);
const _kBorderGreen = Color(0xFF33415F);

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  User? _user;
  Map<String, dynamic>? _userData;
  bool _isLoading = true;
  bool _isUploading = false;

  final _nameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    _user = FirebaseAuth.instance.currentUser;
    if (_user != null) {
      try {
        final doc = await FirebaseFirestore.instance
            .collection('users')
            .doc(_user!.uid)
            .get();
        if (doc.exists) {
          final data = doc.data();
          if (mounted) {
            setState(() {
              _userData = data;
              _nameController.text =
                  data?['name'] ?? _user?.displayName ?? '';
            });
          }

          // Auto-heal: If photo_base64 is missing, try to fetch it from photoURL
          if (data != null && data['photo_base64'] == null) {
            final photoUrl = _user?.photoURL ?? data['photo_url'];
            if (photoUrl != null) {
              _fetchAndStoreProfileImage(photoUrl);
            }
          }
        }
      } catch (e) {
        debugPrint('Error loading user data via Settings: $e');
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _fetchAndStoreProfileImage(String url) async {
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        final base64Image = base64Encode(response.bodyBytes);
        await FirebaseFirestore.instance
            .collection('users')
            .doc(_user!.uid)
            .update({'photo_base64': base64Image});
        
        if (mounted) {
          setState(() {
            _userData?['photo_base64'] = base64Image;
          });
        }
      }
    } catch (e) {
      debugPrint('Error auto-healing profile image in Settings: $e');
    }
  }

  Widget _buildAvatar(double radius, {bool isLarge = false}) {
    final displayName = _user?.displayName ?? _userData?['name'] ?? 'User';
    final initial = displayName.isNotEmpty ? displayName[0].toUpperCase() : 'U';
    final photoBase64 = _userData?['photo_base64'];
    final photoUrl = _user?.photoURL ?? _userData?['photo_url'];

    return CircleAvatar(
      radius: radius,
      backgroundColor: _kBgCard,
      child: ClipOval(
        child: photoBase64 != null
            ? Image.memory(
                base64Decode(photoBase64),
                fit: BoxFit.cover,
                width: radius * 2,
                height: radius * 2,
                errorBuilder: (context, error, stackTrace) => _initialsWidget(initial, isLarge),
              )
            : photoUrl != null
                ? Image.network(
                    photoUrl,
                    fit: BoxFit.cover,
                    width: radius * 2,
                    height: radius * 2,
                    errorBuilder: (context, error, stackTrace) => _initialsWidget(initial, isLarge),
                  )
                : _initialsWidget(initial, isLarge),
      ),
    );
  }

  Widget _initialsWidget(String initial, bool isLarge) {
    return Center(
      child: Text(
        initial,
        style: GoogleFonts.outfit(
          fontSize: isLarge ? 48 : 20,
          fontWeight: FontWeight.bold,
          color: _kTextSecondary,
        ),
      ),
    );
  }

  // ── Profile Photo Logic ────────────────────────────────────────────────
  Future<void> _pickAndUploadImage() async {
    final picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 512,
      maxHeight: 512,
      imageQuality: 75,
    );

    if (image == null) return;

    setState(() => _isUploading = true);

    try {
      // Use readAsBytes() for cross-platform support (Web & Mobile)
      final data = await image.readAsBytes();
      
      // Convert to Base64 for Firestore storage (Free alternative)
      final String base64Image = base64Encode(data);

      // Update Firestore
      await FirebaseFirestore.instance
          .collection('users')
          .doc(_user!.uid)
          .update({
            'photo_base64': base64Image,
            'photo_url': FieldValue.delete(), // Remove old URL reference if any
          });

      await _loadUserData(); // Reload to show new image

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile photo updated!')),
        );
      }
    } catch (e) {
      debugPrint('Error saving image: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save image: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isUploading = false);
    }
  }

  // ── Edit Name Logic ────────────────────────────────────────────────────
  Future<void> _updateName() async {
    final newName = _nameController.text.trim();
    if (newName.isEmpty) return;

    try {
      // Update Auth
      await _user?.updateDisplayName(newName);

      // Update Firestore
      await FirebaseFirestore.instance
          .collection('users')
          .doc(_user!.uid)
          .update({'name': newName});

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Name updated successfully!')),
        );
        FocusScope.of(context).unfocus();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update name: $e')),
        );
      }
    }
  }

  // ── Password Reset Logic ───────────────────────────────────────────────
  Future<void> _sendPasswordReset() async {
    if (_user?.email == null) return;
    try {
      await FirebaseAuth.instance.sendPasswordResetEmail(email: _user!.email!);
      if (mounted) {
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Password Reset'),
            content: Text('A password reset link has been sent to ${_user!.email}'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('OK'),
              )
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  // ── Delete Account Logic ───────────────────────────────────────────────
  Future<void> _deleteAccount() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Account?'),
        content: const Text(
          'This action cannot be undone. All your data will be permanently deleted.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        if (_user != null) {
          await FirebaseFirestore.instance
              .collection('users')
              .doc(_user!.uid)
              .delete();
          await _user?.delete();
        }
        if (mounted) {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (context) => const LoginPage()),
            (route) => false,
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error deleting account: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: _kBgDark,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: _kBgDark,
      appBar: AppBar(
        title: Text(
          'Settings',
          style: GoogleFonts.outfit(fontWeight: FontWeight.w600),
        ),
        backgroundColor: _kBgDark,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // ── Profile Photo Section ────────────────────────────────────
            Center(
              child: Stack(
                children: [
                  _buildAvatar(60, isLarge: true),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: GestureDetector(
                      onTap: _isUploading ? null : _pickAndUploadImage,
                      child: Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: _kGreen,
                          shape: BoxShape.circle,
                          border: Border.all(color: _kBgDark, width: 3),
                        ),
                        child: _isUploading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.camera_alt,
                                size: 20, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // ── Account Settings ─────────────────────────────────────────
            _SectionHeader(title: 'Account'),
            const SizedBox(height: 16),
            _SettingsCard(
              children: [
                // Edit Name
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Row(
                    children: [
                      const Icon(Icons.person_outline, color: _kTextSecondary),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextField(
                          controller: _nameController,
                          style: GoogleFonts.inter(color: _kTextPrimary),
                          decoration: InputDecoration(
                            hintText: 'Display Name',
                            hintStyle:
                                GoogleFonts.inter(color: _kTextSecondary),
                            border: InputBorder.none,
                          ),
                          onSubmitted: (_) => _updateName(),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.check, color: _kGreen),
                        onPressed: _updateName,
                        tooltip: 'Save Name',
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1, color: _kBorderGreen),
                
                // Change Email (disabled for now or visual only)
                ListTile(
                  leading: const Icon(Icons.email_outlined,
                      color: _kTextSecondary),
                  title: Text(
                    _user?.email ?? 'No Email',
                    style: GoogleFonts.inter(color: _kTextSecondary),
                  ),
                  trailing: const Icon(Icons.lock_outline,
                      size: 16, color: _kTextSecondary), // Locked
                ),
                const Divider(height: 1, color: _kBorderGreen),

                // Change Password
                ListTile(
                  leading:
                      const Icon(Icons.vpn_key_outlined, color: _kTextSecondary),
                  title: Text('Change Password',
                      style: GoogleFonts.inter(color: _kTextPrimary)),
                  trailing: const Icon(Icons.arrow_forward_ios,
                      size: 16, color: _kTextSecondary),
                  onTap: _sendPasswordReset,
                ),
              ],
            ),
            const SizedBox(height: 32),

            // ── Preferences ──────────────────────────────────────────────
            _SectionHeader(title: 'Preferences'),
            const SizedBox(height: 16),
            _SettingsCard(
              children: [
                SwitchListTile(
                  secondary: const Icon(Icons.notifications_outlined,
                      color: _kTextSecondary),
                  title: Text('Notifications',
                      style: GoogleFonts.inter(color: _kTextPrimary)),
                  value: _userData?['notifications_enabled'] ?? true,
                  activeColor: _kGreen,
                  onChanged: (val) async {
                    setState(() {
                      if (_userData == null) _userData = {};
                      _userData!['notifications_enabled'] = val;
                    });
                     await FirebaseFirestore.instance
                        .collection('users')
                        .doc(_user!.uid)
                        .update({'notifications_enabled': val});
                  },
                ),
                 const Divider(height: 1, color: _kBorderGreen),
                 SwitchListTile(
                  secondary: const Icon(Icons.dark_mode_outlined,
                      color: _kTextSecondary),
                  title: Text('Dark Mode',
                      style: GoogleFonts.inter(color: _kTextPrimary)),
                  value: true, // Hardcoded for now
                  activeColor: _kGreen,
                  onChanged: (val) {
                     // No-op for now as app is dark only
                  },
                ),
              ],
            ),
            const SizedBox(height: 32),

            // ── Danger Zone ──────────────────────────────────────────────
            _SectionHeader(title: 'Danger Zone', color: Colors.redAccent),
            const SizedBox(height: 16),
            _SettingsCard(
              borderColor: Colors.redAccent.withOpacity(0.3),
              children: [
                ListTile(
                  leading: const Icon(Icons.delete_forever,
                      color: Colors.redAccent),
                  title: Text('Delete Account',
                      style: GoogleFonts.inter(color: Colors.redAccent)),
                  onTap: _deleteAccount,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.color});
  final String title;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title.toUpperCase(),
        style: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.5,
          color: color ?? _kTextSecondary,
        ),
      ),
    );
  }
}

class _SettingsCard extends StatelessWidget {
  const _SettingsCard({required this.children, this.borderColor});
  final List<Widget> children;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: _kBgCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor ?? _kBorderGreen),
      ),
      child: Column(
        children: children,
      ),
    );
  }
}
