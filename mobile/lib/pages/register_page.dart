import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/auth/auth_bloc.dart';

import '../widgets/register_form.dart';

class RegisterPage extends StatelessWidget {
  static const routeName = '/register';
  @override
  Widget build(BuildContext context) {
    final double registerTextSize = MediaQuery.of(context).size.width * 0.1;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: SafeArea(
          child: Column(
            children: [
              Container(
                height: MediaQuery.of(context).size.height * 0.4,
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/images/sign_up.jpg'),
                    fit: BoxFit.contain,
                  ),
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(left: 32),
                    child: Text(
                      'Sign Up',
                      style: TextStyle(
                          fontSize: registerTextSize,
                          fontWeight: FontWeight.bold,
                          color: Color.fromARGB(255, 0, 0, 85)),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: BlocProvider(
                      create: (context) => AuthBloc(),
                      child: RegisterForm(),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
