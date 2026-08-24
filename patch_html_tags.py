import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

bad_html = """                      </div>
                    </div>
                  </div>
                  </div>
                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->"""

good_html = """                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->"""

# Let's count them precisely from the file to ensure exact match.
# The actual content has:
#                     </div>
#                   </div>
#                   </div>
#                 </div>

html = html.replace(
"""                    </div>
                  </div>
                  </div>
                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->""",
"""                    </div>
                  </div>
                </div>
                
                <!-- Secondary views (scraped pages templates rendered on nav clicks) -->"""
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Removed extra </div> tags that broke the layout.")
