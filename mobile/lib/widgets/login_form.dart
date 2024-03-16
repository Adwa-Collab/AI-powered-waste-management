import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/auth/auth_bloc.dart';
import '../blocs/auth/auth_event.dart';
import '../blocs/auth/auth_state.dart';
import '../pages/register_page.dart';
import '../constants/login_form_constants.dart';

class LoginForm extends StatefulWidget {
  @override
  _LoginFormState createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isPasswordVisible = false;

  @override
  Widget build(BuildContext context) {
    final authBloc = BlocProvider.of<AuthBloc>(context);

    final double buttonWidth =
        MediaQuery.of(context).size.width * LoginFormConstants.buttonWidth;
    final double buttonHeight =
        MediaQuery.of(context).size.height * LoginFormConstants.buttonHeight;
    final double sizedBoxHeight =
        MediaQuery.of(context).size.height * LoginFormConstants.sizedBoxHeight;

    final IconData emailIcon = LoginFormConstants.emailIcon;
    final IconData passwordIcon = LoginFormConstants.passwordIcon;

    final double iconOpacity = LoginFormConstants.iconOpacity;
    final double inputFieldOpacity = LoginFormConstants.inputFieldOpacity;

    final TextStyle buttonTextStyle = LoginFormConstants.buttonTextStyle;
    final TextStyle linkButtonStyle = LoginFormConstants.linkButtonStyle;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Opacity(
                opacity: iconOpacity,
                child: Icon(emailIcon),
              ),
              SizedBox(width: 20),
              Expanded(
                child: Opacity(
                  opacity: inputFieldOpacity,
                  child: TextField(
                    controller: _usernameController,
                    decoration: InputDecoration(
                      labelText: 'Username',
                    ),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: sizedBoxHeight),
          Row(
            children: [
              Opacity(
                opacity: iconOpacity,
                child: Icon(passwordIcon),
              ),
              SizedBox(width: 20),
              Expanded(
                child: Opacity(
                  opacity: inputFieldOpacity,
                  child: TextField(
                    controller: _passwordController,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      suffixIcon: IconButton(
                        icon: Icon(
                          _isPasswordVisible
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _isPasswordVisible = !_isPasswordVisible;
                          });
                        },
                      ),
                    ),
                    obscureText: !_isPasswordVisible,
                  ),
                ),
              ),
            ],
          ),
          BlocBuilder<AuthBloc, AuthState>(
            builder: (context, state) {
              if (state is AuthLoadingState) {
                return Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: Text(
                    'Connecting...',
                    style: TextStyle(color: Colors.blueAccent),
                  ),
                );
              } else if (state is AuthErrorState) {
                return Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: Text(
                    state.errorMessage,
                    style: TextStyle(color: Colors.red),
                  ),
                );
              }
              return SizedBox.shrink();
            },
          ),
          SizedBox(height: sizedBoxHeight),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: () {},
                style: ButtonStyle(
                  padding: MaterialStateProperty.all(EdgeInsets.zero),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  'Forget Password?',
                  style: linkButtonStyle,
                ),
              ),
            ],
          ),
          SizedBox(height: sizedBoxHeight),
          Container(
            width: buttonWidth,
            height: buttonHeight,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
            ),
            child: ElevatedButton(
              onPressed: () {
                authBloc.add(LoginEvent(
                  _usernameController.text,
                  _passwordController.text,
                  context,
                ));
              },
              style: ElevatedButton.styleFrom(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                'Login',
                style: buttonTextStyle,
              ),
            ),
          ),
          SizedBox(
            height: 16,
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Don\'t have an account?',
                style: TextStyle(
                    fontSize: 16, color: Color.fromARGB(188, 117, 117, 117)),
              ),
              SizedBox(
                width: 5,
              ),
              TextButton(
                onPressed: () {
                  Navigator.pushNamed(context, RegisterPage.routeName);
                },
                style: ButtonStyle(
                  padding: MaterialStateProperty.all(EdgeInsets.zero),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  'Register',
                  style: linkButtonStyle,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
