# Be sure to restart your server when you modify this file.

# Your secret key for verifying cookie session data integrity.
# If you change this key, all old sessions will become invalid!
# Make sure the secret is at least 30 characters and all random, 
# no regular words or you'll be exposed to dictionary attacks.
ActionController::Base.session = {
  :key         => '_DB_Reader_IOvirt_session',
  :secret      => '78acb13b00cc7c224fe48eabe0a6e001080e504eac7a8685c3d539e4a10a88f7bd67b82a2f76fef19324e0d18af337a94b953d599d5d142fa4d283eb6a767a4f'
}

# Use the database for sessions instead of the cookie-based default,
# which shouldn't be used to store highly confidential information
# (create the session table with "rake db:sessions:create")
# ActionController::Base.session_store = :active_record_store
